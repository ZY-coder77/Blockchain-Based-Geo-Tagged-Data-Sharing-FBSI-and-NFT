// SPDX-License-Identifier: GPL-3.0

pragma solidity ^0.8.0;


/**
 * @dev Nonuniform partition-tree，简称NUP-tree(由Quad-tree改进而来) + Inverted file table.
 * Inverted file table的表项由调用合约声明
 * 在树上的查询也由调用合约实现
 * 本library提供树结构和插入、删除操作，节点对应的Inverted file table将由调用合约维护，包括它的删除
 */
library NUP_tree {
    //tokens' authenticated data structure(ADS) modified Quad-tree(改进为Nonuniform partition-tree，简称NUP-tree) + Inverted file table
    
    //NUP-tree节点
    struct TreeNode{
        
        int64[] boundaryList;
        uint64[] childNodeList;

        uint64 parentPointer;
        
        //节点所在层数，用于计算节点分区的维度
        uint8 layer;
        //是父节点的第几个子节点，0表示第一个，1表示第二个
        uint8 sequenceNumber;
    }

    //二维地图上的矩形区域结构
    struct SquareRange{
        int64 leftLongitude;
        int64 rightLongitude;
        int64 downLatitude;
        int64 topLatitude;
    }
    
    //分裂类型
    enum SplitType{CHILD, BROTHER}

    /*
     *@dev NUP树-分裂节点,只有叶节点可以分裂
     * 1. 同级分裂出来的节点(右节点)要定义为叶节点,右节点要插入父节点的partition List
     * 2. 下级分裂:原节点修改为非叶节点,新分裂出来的两个节点插入父节点的partition List
     *参数：
     *    1. whileTree：整棵树的mapping
     *    2. indexTarget：待分裂节点在树mapping中的关键字
     *    3. splitPoint:分裂点的坐标
     *    4. splitType：分裂类型，同级分裂还是下级分裂
     *    5. sumNode:当前树中的节点数
     *返回值： bool:指示分裂成功与否
     *注：1. 调用者自己在调用结束后指定分裂后的左节点和右节点的倒排文件列表
     *    2.同级分裂出的左节点keyword不变，右节点keyword为分裂前的sumNode
     *    3.下级分裂出的左节点keyword为分裂前的sumNode，右节点为分裂前的sumNode+1
     *    4.分裂点是否在待分裂节点的区域边界内,由调用者在调用前验证,因为调用者从根节点搜索下来,能够确定待分裂节点区域的4个边界
    */
    function _splitNode(mapping(uint64=>TreeNode) storage wholeTree, uint64 indexTarget,int64 splitPoint, 
                        SplitType splitType,uint64 sumNode) public returns(bool){
        
        //检查是否为叶节点
        require(wholeTree[indexTarget].childNodeList.length==0,"E-NL");//The node is not a leaf node!
        //同级分裂
        if(splitType==SplitType.BROTHER)
        {
            TreeNode storage leftNode=wholeTree[indexTarget];
            TreeNode storage rightNode=wholeTree[sumNode];
            TreeNode storage parentNode=wholeTree[leftNode.parentPointer];
            
            rightNode.parentPointer=leftNode.parentPointer;
            rightNode.sequenceNumber=leftNode.sequenceNumber+1;
            rightNode.layer=leftNode.layer;

            /*
             *在待分裂节点的父节点中插入rightNode的分区信息
            */
            uint8 index=uint8(parentNode.childNodeList.length-1);
            uint8 NumberInBack=uint8(index-leftNode.sequenceNumber);

            //如果待分裂节点是其父节点的最后一个子节点
            if(NumberInBack==0){
                parentNode.childNodeList.push(sumNode);
                parentNode.boundaryList.push(splitPoint);

            }
            else{
                //原本在leftNode之后的同级节点在父节点的partitionList数组中的位置必须退1//
                wholeTree[parentNode.childNodeList[index]].sequenceNumber++;
                parentNode.childNodeList.push(parentNode.childNodeList[index]);
                parentNode.boundaryList.push(parentNode.boundaryList[index-1]);
                
                for(uint8 i=1;i<NumberInBack;i=i+1){
                    wholeTree[parentNode.childNodeList[index-i]].sequenceNumber++;
                    parentNode.childNodeList[index-i+1]=parentNode.childNodeList[index-i];
                    parentNode.boundaryList[index-i]=parentNode.boundaryList[index-i-1];
                }
                //将右节点的信息添加到父节点中
                parentNode.childNodeList[leftNode.sequenceNumber+1]=sumNode;
                parentNode.boundaryList[leftNode.sequenceNumber]=splitPoint;
            }
            
            return true;        
        }
        //下级分裂
        else{
            //待分裂节点成为父节点
            TreeNode storage parentNode=wholeTree[indexTarget];
            TreeNode storage leftNode=wholeTree[sumNode];
            TreeNode storage rightNode=wholeTree[sumNode+1];

            //父节点的childNodeList和boundaryList中添加元素增加左右节点和分界线
            parentNode.childNodeList.push(sumNode);
            parentNode.childNodeList.push(sumNode+1);
            parentNode.boundaryList.push(splitPoint);

            //定义左右节点的父节点和作为子节点的排序、所在层
            leftNode.parentPointer=indexTarget;
            leftNode.sequenceNumber=0;
            leftNode.layer=parentNode.layer+1;
            
            rightNode.parentPointer=indexTarget;
            rightNode.sequenceNumber=1;
            rightNode.layer=leftNode.layer;

            return true;
        }
    }


    /*
     *@dev NUP树-删除节点,给定一个节点进行删除操作
     * 1.只有叶节点可以删除
     * 2.删除这个节点后,如果父节点只剩一个子节点,那么要将剩下的唯一子节点合并到父节点,使父节点成为叶节点
     * 3.删除节点后,要将后面的同级节点在父节点中的顺序前移
     * 4.第一子节点删除后，原空间向后合并，因此要删除第一个分界线；其余节点删除后，原空间向前合并，因此要删除与其排序小1的分界线
     * 删除节点不可更改总结点数
    */
    function _deleteNode(mapping(uint256=>TreeNode) storage wholeTree, uint256 indexTarget) public returns(bool){
        //检查是否为叶节点//childNodeList.length==0
        require(wholeTree[indexTarget].childNodeList.length==0,"E-NL");//The node is not a leaf node!

        TreeNode storage parentNode=wholeTree[wholeTree[indexTarget].parentPointer];
        
        uint256 i=wholeTree[indexTarget].sequenceNumber+1;

        //待删除节点是第一个子节点
        if(i==1){
            wholeTree[parentNode.childNodeList[1]].sequenceNumber--;
            parentNode.childNodeList[0]=parentNode.childNodeList[1];
            i=2;
        }
        
        //将待删除节点后的节点前移一个位置
        for(i;i<parentNode.childNodeList.length;i++){
            wholeTree[parentNode.childNodeList[i]].sequenceNumber--;
            parentNode.childNodeList[i-1]=parentNode.childNodeList[i];
            parentNode.boundaryList[i-2]=parentNode.boundaryList[i-1];
        }    
        //释放节点中的数组和父节点的childNodeList和boundaryList中的最后一个位置
        delete wholeTree[indexTarget];
        parentNode.childNodeList.pop();
        parentNode.boundaryList.pop();

        //处理父节点剩余子节点是否只有一个的情况:子节点取代父节点，修改子节点和祖父节点的指针
        if(parentNode.childNodeList.length==1){
            wholeTree[parentNode.childNodeList[0]].sequenceNumber=parentNode.sequenceNumber;
            wholeTree[parentNode.childNodeList[0]].parentPointer=parentNode.parentPointer;
            wholeTree[parentNode.parentPointer].childNodeList[parentNode.sequenceNumber]=parentNode.childNodeList[0];
        }
        return true;
    }
    
    /*
     *在NUP_tree查找一个点位置所属区域(叶节点)
     *参数:
     *  1. whileTree：整棵树的mapping
     *  2. longitude,latitude:查询点的坐标
     *返回值:节点在mapping中的关键字
    */
    function _findPointInTree(mapping(uint64=>TreeNode) storage wholeTree,SquareRange memory limitSquareRange,
                              int64 longitude, int64 latitude) public returns(uint64 indexNode){
        //定义根节点在mapping结构类型下的NUP_tree中的关键字
        uint64 indexRoot=0;
        
        //检查输入合法性
        require(longitude>=limitSquareRange.leftLongitude,"E1");//Input longitude is too low!
        require(longitude<=limitSquareRange.rightLongitude,"E2");//Input longitude is too high!
        require(latitude>=limitSquareRange.downLatitude,"E3");//Input latitude is too low!
        require(latitude<=limitSquareRange.topLatitude,"E4");//Input latitude is too high!

        return _findPointInTree(wholeTree,indexRoot,longitude, latitude);
    }

    /*
     *在NUP_tree查找一个点位置所属区域(叶节点)
     *参数:
     *  1. whileTree：整棵树的mapping
     *  2. indexBranch:待查找分支在whileTree中的根索引
     *  3. branchSquareRange:待查找分支的根表示的空间范围
     *  4. longitude,latitude:查询点的坐标
     *返回值:节点在mapping中的关键字
    */
    function _findPointInTree(mapping(uint64=>TreeNode) storage wholeTree,uint64 indexBranch, int64 longitude,int64 latitude)
                                   public returns(uint64 indexNode){
        //如果是叶节点,返回index Branch
        if(wholeTree[indexBranch].childNodeList.length==0){
            return indexBranch;
        }

        TreeNode storage branchRoot=wholeTree[indexBranch];

        //查找分支的根节点是经度划分,找到最符合查询点坐标的下一层节点
        uint64 childListIndex;
        if(branchRoot.layer%2==0){
            //childListIndex = uint64(_binarySearch(branchRoot.boundaryList, longitude));
            childListIndex = uint64(_sequentialSearch(branchRoot.boundaryList, longitude));
        }
        else{//查找分支的根节点是纬度划分,找到最符合查询点坐标的下一层节点
            //childListIndex = uint64(_binarySearch(branchRoot.boundaryList, latitude));
            childListIndex = uint64(_sequentialSearch(branchRoot.boundaryList, latitude));
        }
        return _findPointInTree(wholeTree, branchRoot.childNodeList[childListIndex], longitude, latitude);
    }

    /*二分法，返回下一个子节点在子节点列表中的序号*/
    function  _binarySearch(int64[] storage List, int64 target) view public returns(uint256 index){
        require(List.length>0);
        //列表的长度默认用uint256表示
        //当target<List[0]时，二分法的最后将出现high=-1的情况，uint256不能表示，因此提前排除此情况
        if(target<=List[0]){
            return 0;
        }/*
        if(List.length==1){
            return 1;
        }*/
        uint8 low = 0;
        uint8 high = uint8(List.length-1);
        uint8 mid;
        while(low<high){
            mid = (low + high)/2;
            if(target<List[mid]){
                high = mid - 1;
            }
            else if(target>List[mid]){
                low = mid + 1;
            }
            else{
                return mid;
            }
        }
        if(target<=List[low]){
        return low;
        }
        else{
            return low+1;
        }
    }

    /*顺序查找，返回下一个子节点在子节点列表中的序号*/
    function  _sequentialSearch(int64[] storage List, int64 target) view public returns(uint256 index){
        require(List.length>0,"Length is 0!");
        //列表的长度默认用uint256表示
        for(uint256 i =0;i<List.length;i++){
            if(target<=List[i]){
                return i;
            }
        }        
        return List.length;
    }

    /*
     *在NUP_tree查找一个矩形区域所属叶节点列表
     *参数:
     *  1. whileTree：整棵树的mapping
     *  2. squareTarget:需要被查找的矩形区域
     *  3. resultList:保存目标矩形区域覆盖的叶节点在mapping类型的NUP_tree中的关键字的数组
    */
    function _findSquareInTree(mapping(uint64=>TreeNode) storage wholeTree,SquareRange memory limitSquareRange,
                                    SquareRange memory squareTarget, uint64[] storage resultList) public {
        //定义根节点在mapping token_NUP_tree中的关键字
        uint64 indexRoot=0;
        
        //检查输入合法性
        require(squareTarget.leftLongitude<=squareTarget.rightLongitude,"E5");//Input longitude is wrong!
        require(squareTarget.leftLongitude>=limitSquareRange.leftLongitude,"E6");//Input left longitude is too low!
        require(squareTarget.rightLongitude<=limitSquareRange.rightLongitude,"E7");//Input right longitude is too high!

        require(squareTarget.downLatitude<=squareTarget.topLatitude,"E8");//Input latitude is wrong!
        require(squareTarget.downLatitude>=limitSquareRange.downLatitude,"E9");//Input down latitude is too low!
        require(squareTarget.topLatitude<=limitSquareRange.topLatitude,"E10");//Input top latitude is too high!
        
        //清空resultList
        while(resultList.length!=0){
            resultList.pop();
        }
        _findSquareInTree(wholeTree,indexRoot,limitSquareRange,squareTarget,resultList);
    }

    /*
     *在NUP_tree查找一个矩形区域所属叶节点列表
     *参数:
     *  1. whileTree:整棵树的mapping
     *  2. indexBranch:待查找分支在whileTree中的根索引
     *  3. branchSquareRange:待查找分支的根表示的空间范围
     *  4. targetSquareRange:查询目标矩形的空间范围
     *  5. resultList:保存目标矩形区域覆盖的叶节点在mapping类型的NUP_tree中的关键字的数组
    */
    function _findSquareInTree(mapping(uint64=>TreeNode) storage wholeTree,uint64 indexBranch,
                                   SquareRange memory branchSquareRange,SquareRange memory targetSquareRange,
                                   uint64[] storage resultList) public returns(bool compeletion){        
        //如果是叶节点,在resultList中添加该节点索引indexBranch，并结束该分支点递归过程
        if(wholeTree[indexBranch].childNodeList.length==0){
            resultList.push(indexBranch);
            return true;
        }

        TreeNode memory branchRoot=wholeTree[indexBranch];
        //子节点的区域大小初始化为父节点(分支根)的区域大小
        SquareRange memory childrenSquareRange=branchSquareRange; 

        //查找分支的根节点的下一级节点是经度划分,所有与目标矩形区域有覆盖的子节点进行递归查找,整合子节点们的查找结果
        if(branchRoot.layer%2==0){
            //每一个子节点都要遍历，但是要单独先处理第一个，然后是中间几个，最后处理最后一个
            bool haveCovered=false;
            //先处理第一个子节点
            childrenSquareRange.rightLongitude=branchRoot.boundaryList[0]; 
            if(isCovered(targetSquareRange,childrenSquareRange)){
                _findSquareInTree(wholeTree,branchRoot.childNodeList[0],childrenSquareRange,targetSquareRange,
                                resultList);
                haveCovered=true;
            }
            //处理中间节点
            uint8 i=1;
            for(i;i<branchRoot.childNodeList.length-1;i++){
                //确定子节点边界，如果子节点与矩形覆盖，则向下一层查找，否在右移子节点范围边界            
                childrenSquareRange.leftLongitude=branchRoot.boundaryList[i-1];
                childrenSquareRange.rightLongitude=branchRoot.boundaryList[i];
                if(isCovered(targetSquareRange,childrenSquareRange)){
                    _findSquareInTree(wholeTree,branchRoot.childNodeList[i],childrenSquareRange,targetSquareRange,
                                resultList);
                    haveCovered=true;
                }
                else{
                    if(haveCovered){
                        break;
                    }
                }
            }
            //单独处理最后一个子节点
            if(i==branchRoot.childNodeList.length-1){
                childrenSquareRange.leftLongitude=branchRoot.boundaryList[i-1];
                childrenSquareRange.rightLongitude=branchSquareRange.rightLongitude;
                if(isCovered(targetSquareRange,childrenSquareRange)){
                    _findSquareInTree(wholeTree,branchRoot.childNodeList[i],childrenSquareRange,targetSquareRange,
                                resultList);
                }
            }      
        }
        else{//查找分支的根节点的下一级节点是纬度划分,所有与目标矩形区域有覆盖的子节点进行递归查找,整合子节点们的查找结果
            //二分法查找
            bool haveCovered=false;
            //先处理第一个子节点
            childrenSquareRange.topLatitude=branchRoot.boundaryList[0]; 
            if(isCovered(targetSquareRange,childrenSquareRange)){
                _findSquareInTree(wholeTree,branchRoot.childNodeList[0],childrenSquareRange,targetSquareRange,
                                resultList);
                haveCovered=true;
            }
            //处理中间节点
            uint8 i=1;
            for(i;i<branchRoot.childNodeList.length-1;i++){
                //确定子节点边界，如果子节点与矩形覆盖，则向下一层查找，否在右移子节点范围边界            
                childrenSquareRange.downLatitude=branchRoot.boundaryList[i-1];
                childrenSquareRange.topLatitude=branchRoot.boundaryList[i];
                if(isCovered(targetSquareRange,childrenSquareRange)){
                    _findSquareInTree(wholeTree,branchRoot.childNodeList[i],childrenSquareRange,targetSquareRange,
                                resultList);
                    haveCovered=true;
                }
                else{
                    if(haveCovered){
                        break;
                    }
                }
            }
            //单独处理最后一个子节点
            if(i==branchRoot.childNodeList.length-1){
                childrenSquareRange.downLatitude=branchRoot.boundaryList[i-1];
                childrenSquareRange.topLatitude=branchSquareRange.topLatitude;
                if(isCovered(targetSquareRange,childrenSquareRange)){
                    _findSquareInTree(wholeTree,branchRoot.childNodeList[i],childrenSquareRange,targetSquareRange,
                                resultList);
                }
            }
        }
    }

    /*
     *@dev 通过节点编号（keyword）计算该节点的区域范围
     * 1. wholeTree:要查找的树
     * 2. indexNode：要查找的节点
     * 3. existingRange：已经查到的范围
     * 4. left，right，down，top：existingRange中哪些边是确定的
    */
    function rangeOfNode(mapping(uint64=>TreeNode) storage wholeTree,SquareRange memory limitSquareRange,uint64 indexNode, 
                        SquareRange memory existingRange,bool left, bool right, bool down, bool top) 
                        public returns(SquareRange memory nodeRange){

        //目标节点为根节点
        if(indexNode==0){
            if(left==false)
                existingRange.leftLongitude=limitSquareRange.leftLongitude;
            if(right==false)
                existingRange.rightLongitude=limitSquareRange.rightLongitude;
            if(down==false)
                existingRange.downLatitude=limitSquareRange.downLatitude;
            if(top==false)
                existingRange.topLatitude=limitSquareRange.topLatitude;     
            return existingRange;
        }

        TreeNode storage parentNode=wholeTree[wholeTree[indexNode].parentPointer];
        uint8 sequence=wholeTree[indexNode].sequenceNumber;
        //是第一个子节点
        if(sequence==0){
            if(parentNode.layer%2==0){//父节点是经度层且右经度未确定
                if(right==false){
                    right=true;
                    existingRange.rightLongitude=parentNode.boundaryList[0];
                }
            }
            else{//父节点是纬度层且上纬度未确定
                if(top==false){
                    top=true;
                    existingRange.topLatitude=parentNode.boundaryList[0];
                }
            }
        }
        else if(sequence==parentNode.childNodeList.length-1){//是最后一个子节点
            if(parentNode.layer%2==0){//父节点是经度层且左经度未确定
                if(left==false){
                    left=true;
                    existingRange.leftLongitude=parentNode.boundaryList[sequence];
                }
            }
            else{//父节点是纬度层且下纬度未确定
                if(down==false){
                    down=true;
                    existingRange.downLatitude=parentNode.boundaryList[sequence];
                }
            }
        }
        else{
            if(parentNode.layer%2==0){//父节点是经度层
                if(left==false){
                    left=true;
                    existingRange.leftLongitude=parentNode.boundaryList[sequence-1];
                }
                if(right==false){
                    right=true;
                    existingRange.rightLongitude=parentNode.boundaryList[sequence];
                }
            }
            else{//父节点是纬度层
                if(down==false){
                    down=true;
                    existingRange.downLatitude=parentNode.boundaryList[sequence-1];
                }
                if(top==false){
                    top=true;
                    existingRange.topLatitude=parentNode.boundaryList[sequence];
                }
            }
        }

        if(left&&right&&down&&top)
            return existingRange;
        else    
            rangeOfNode(wholeTree,limitSquareRange, wholeTree[indexNode].parentPointer,
                         existingRange, left, right, down, top);        
    }


    function lowBoundaryOfNode(mapping(uint64=>TreeNode) storage wholeTree,SquareRange memory limitSquareRange,
                        uint64 indexNode, int64 leftLongitude,int64 downLatitude,bool left, bool down) 
                        public returns(int64 lon,int64 lat){

        //父节点为根节点
        if(indexNode==0){
            if(left==false)
                leftLongitude=limitSquareRange.leftLongitude;
            
            if(down==false)
                downLatitude=limitSquareRange.downLatitude;
            
            return (leftLongitude,downLatitude);
        }

        TreeNode memory parentNode=wholeTree[wholeTree[indexNode].parentPointer];
        uint8 sequence=wholeTree[indexNode].sequenceNumber;
       
       if(sequence==parentNode.childNodeList.length-1){//是最后一个子节点
            if(parentNode.layer%2==0){//父节点是经度层且左经度未确定
                if(left==false){
                    left=true;
                    leftLongitude=parentNode.boundaryList[sequence-1];
                }
            }
            else{//父节点是纬度层且下纬度未确定
                if(down==false){
                    down=true;
                    downLatitude=parentNode.boundaryList[sequence-1];
                }
            }
        }
        else{
            if(parentNode.layer%2==0){//父节点是经度层
                if(left==false){
                    left=true;
                    leftLongitude=parentNode.boundaryList[sequence-1];
                }
            }
            else{//父节点是纬度层
                if(down==false){
                    down=true;
                    downLatitude=parentNode.boundaryList[sequence-1];
                }
            }
        }

        if(left&&down)
            return (leftLongitude,downLatitude);
        else    
            lowBoundaryOfNode(wholeTree,limitSquareRange, wholeTree[indexNode].parentPointer,
                        leftLongitude,downLatitude, left, down);        
    }

    /*
     *@dev 判断两个区域交叉覆盖
    */
    function isCovered(SquareRange memory squareA,SquareRange memory squareB) public pure returns(bool){
        //B在A的右侧
        if(squareA.rightLongitude<squareB.leftLongitude)
            return false;
        //B在A的左侧
        if(squareB.rightLongitude<squareA.leftLongitude)
            return false;
        //B在A的上方
        if(squareA.topLatitude<squareB.downLatitude)
            return false;
        //B在A的下方
        if(squareB.topLatitude<squareA.downLatitude)
            return false;
        
        //排除不相交，剩下的可能就是相交
        return true;
    }

    //判断指定的点状位置是否落在指定的矩形区域范围内
    function isIncluded(SquareRange memory square,int64 longitude, int64 latitude) public pure returns(bool){
        if(longitude<=square.leftLongitude||longitude>square.rightLongitude
            ||latitude<=square.downLatitude||latitude>square.topLatitude)
            return false;
        return true;
    }
}