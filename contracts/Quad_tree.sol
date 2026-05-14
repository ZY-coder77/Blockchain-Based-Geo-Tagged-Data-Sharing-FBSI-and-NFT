// SPDX-License-Identifier: GPL-3.0

pragma solidity ^0.8.0;


/**
 * @dev Quad tree
 * Inverted file table的表项由调用合约声明
 * 本library提供树结构和节点分裂，节点删除，在树上查找点，在树上查找区域.节点对应的Inverted file table将由调用合约维护
 */
library Quad_tree {
    /*
    struct Boundary{
        int256 line;
        uint256 pointer;
    }*/
    
    //Quad-tree节点
    struct TreeNode{
        uint256 parentPointer;
        uint256[4] childPointerList;

        //是父节点的第几个子节点，0表示第一个，1表示第二个
        uint8 sequenceNumber;
        
        //节点所在层数，用于计算节点分区的维度
        uint8 layer;
    }

    //二维地图上的矩形区域结构
    struct SquareRange{
        int256 leftLongitude;
        int256 rightLongitude;
        int256 downLatitude;
        int256 topLatitude;
    }

    /*
     *@dev Quad tree-分裂节点,只有叶节点可以分裂
     * 1. 只有下级分裂
     * 2. 原节点修改为非叶节点,新分裂出来的4个节点插入父节点的childPointerList
     *参数：
     *    1. whileTree：整棵树的mapping
     *    2. indexTarget：待分裂节点在树mapping中的关键字
     *    3. sumNode:当前树中的节点数
     *返回值： bool:指示分裂成功与否
     *注：1. 调用者自己在调用结束后指定分裂后的节点的倒排文件列表
     *    2. 分裂出的左起第一个节点keyword为分裂前的sumNode，此后依次+1
    */
    function _splitNode(mapping(uint256=>TreeNode) storage wholeTree, uint256 indexTarget,
                        uint256 sumNode) public returns(bool){
        
        //检查是否为叶节点
        require(wholeTree[indexTarget].childPointerList[0]==0,"E-NL");//The node is not a leaf node!
        
        //待分裂节点成为父节点
        TreeNode storage parentNode=wholeTree[indexTarget];
        TreeNode storage firstNode=wholeTree[sumNode];
        TreeNode storage secondNode=wholeTree[sumNode+1];
        TreeNode storage thirdNode=wholeTree[sumNode+2];
        TreeNode storage fourthNode=wholeTree[sumNode+3];

        //父节点从叶节点修改为非叶节点,childPointerList指新增的4个节点
        parentNode.childPointerList[0]=sumNode;
        parentNode.childPointerList[1]=sumNode+1;
        parentNode.childPointerList[2]=sumNode+2;
        parentNode.childPointerList[3]=sumNode+3;

        //新增的4个节点定义为叶节点，指定父节点、在兄弟节点间的排序、层数
        firstNode.parentPointer=indexTarget;
        firstNode.childPointerList[0]=0;
        firstNode.sequenceNumber=0;
        firstNode.layer=parentNode.layer+1;

        secondNode.parentPointer=indexTarget;
        secondNode.childPointerList[0]=0;
        secondNode.sequenceNumber=1;
        secondNode.layer=parentNode.layer+1;

        thirdNode.parentPointer=indexTarget;
        thirdNode.childPointerList[0]=0;
        thirdNode.sequenceNumber=2;
        thirdNode.layer=parentNode.layer+1;

        fourthNode.parentPointer=indexTarget;
        fourthNode.childPointerList[0]=0;
        fourthNode.sequenceNumber=3;
        fourthNode.layer=parentNode.layer+1;

        return true;
        
    }


    /*
     *@dev Quad tree-删除节点
     * 1.只有叶节点可以删除
     * 2.要同时删除这个节点的所有兄弟节点
     * 3.删除节点后,其父节点成为叶节点，父节点上附着的tokenIDList和倒排文件由主合同辅助合并
     * 4.因此主合同要确保四个子节点的tokenIDList之和不超过maxItemCount
     * 5.删除节点不可更改总结点数：节点总数后续节点分裂处新节点的keyword
    */
    function _deleteNode(mapping(uint256=>TreeNode) storage wholeTree, 
                    uint256 indexTarget) public returns(bool result){
        //被删节点及其兄弟节点都必须是叶节点
        require(wholeTree[indexTarget].childPointerList[0]==0,"E-NL");//The node is not a leaf node!
        require(wholeTree[indexTarget+1].childPointerList[0]==0,"E-FBNL");//It's first brother node is not a leaf node!
        require(wholeTree[indexTarget+2].childPointerList[0]==0,"E-SBNL");//It's second brother node is not a leaf node!
        require(wholeTree[indexTarget+3].childPointerList[0]==0,"E-TNL");//It's third brother node is not a leaf node!

        TreeNode storage parentNode=wholeTree[wholeTree[indexTarget].parentPointer];
        //依次将父节点的子节点列表清零
        for(uint8 i=0;i<4;i++){
            parentNode.childPointerList[i]=0;
        }

        return true;
    }
    
    /*
     *在Quad tree查找一个点位置所属区域(叶节点)
     *参数:
     *  1. whileTree：整棵树的mapping
     *  2. limitSquareRange: quad最大区域限制
     *  3. longitude,latitude:查询点的坐标
     *返回值:节点在mapping中的关键字
    */
    function _findPointInTree(mapping(uint256=>TreeNode) storage wholeTree,SquareRange memory limitSquareRange,
                              int256 longitude, int256 latitude) public returns(uint256 indexNode){
        //定义根节点在mapping结构类型下的Quad tree中的关键字
        uint256 indexRoot=0;
        
        //检查输入合法性
        require(longitude>=limitSquareRange.leftLongitude,"E1");//Input longitude is too low!
        require(longitude<=limitSquareRange.rightLongitude,"E2");//Input longitude is too high!
        require(latitude>=limitSquareRange.downLatitude,"E3");//Input latitude is too low!
        require(latitude<=limitSquareRange.topLatitude,"E4");//Input latitude is too high!

        return _findPointInTree(wholeTree,indexRoot,limitSquareRange,longitude, latitude);
    }

    /*
     *在在Quad tree查找一个点位置所属区域(叶节点)
     *参数:
     *  1. whileTree：整棵树的mapping
     *  2. indexBranch:待查找分支在whileTree中的根索引
     *  3. branchSquareRange:待查找分支的根表示的空间范围
     *  4. longitude,latitude:查询点的坐标
     *返回值:节点在mapping中的关键字
    */
    function _findPointInTree(mapping(uint256=>TreeNode) storage wholeTree,uint256 indexBranch,
                                   SquareRange memory branchSquareRange,int256 longitude,int256 latitude)
                                   public returns(uint256 indexNode){
        //如果是叶节点,返回index Branch
        if(wholeTree[indexBranch].childPointerList[0]==0){
            return indexBranch;
        }

        //查找4个子节点,找到符合查询点坐标的下一层节点,调整矩形经度范围
        /*------- ---branchSquareRange.topLatitude
         *| D  | C  |
         *|---------|midLatitude
         *| A  | B  |
         *-----------branchSquareRange.downLatitude
          midLongtitude
        */
        int256 midLongitude=(branchSquareRange.leftLongitude+branchSquareRange.rightLongitude)/2;
        int256 midLatitude=(branchSquareRange.downLatitude+branchSquareRange.topLatitude)/2;

        bool isFind = false;
        //在D区
        if(longitude>branchSquareRange.leftLongitude){
            if(longitude<=midLongitude){
                if(latitude>midLatitude){
                    if(latitude<=branchSquareRange.topLatitude){
                        branchSquareRange.leftLongitude=branchSquareRange.leftLongitude;
                        branchSquareRange.rightLongitude=midLongitude;
                        branchSquareRange.downLatitude=midLatitude;
                        branchSquareRange.topLatitude=branchSquareRange.topLatitude;
                        indexBranch=wholeTree[indexBranch].childPointerList[3];
                        isFind = true;
                    }
                }
            }
        }
        //在C区
        if(isFind==false){
            if(longitude>midLongitude){
                if(longitude<=branchSquareRange.rightLongitude){
                    if(latitude>midLatitude){
                        if(latitude<=branchSquareRange.topLatitude){
                            branchSquareRange.leftLongitude=midLongitude;
                            branchSquareRange.rightLongitude=branchSquareRange.rightLongitude;
                            branchSquareRange.downLatitude=midLatitude;
                            branchSquareRange.topLatitude=branchSquareRange.topLatitude;
                            indexBranch=wholeTree[indexBranch].childPointerList[2];
                            isFind = true;
                        }
                    }
                }
            }
        }
        //在B区
        if(isFind==false){
            if(longitude>midLongitude){
                if(longitude<=branchSquareRange.rightLongitude){
                    if(latitude>branchSquareRange.downLatitude){
                        if(latitude<=midLatitude){
                            branchSquareRange.leftLongitude=midLongitude;
                            branchSquareRange.rightLongitude=branchSquareRange.rightLongitude;
                            branchSquareRange.downLatitude=branchSquareRange.downLatitude;
                            branchSquareRange.topLatitude=midLatitude;
                            indexBranch=wholeTree[indexBranch].childPointerList[1];
                            isFind = true;
                        }
                    }
                }
            }
        }
        //在A区
        if(isFind==false){
            if(longitude>branchSquareRange.leftLongitude){
                if(longitude<=midLongitude){
                    if(latitude>branchSquareRange.downLatitude){
                        if(latitude<=midLatitude){
                            branchSquareRange.leftLongitude=branchSquareRange.leftLongitude;
                            branchSquareRange.rightLongitude=midLongitude;
                            branchSquareRange.downLatitude=branchSquareRange.downLatitude;
                            branchSquareRange.topLatitude=midLatitude;
                            indexBranch=wholeTree[indexBranch].childPointerList[0];
                            isFind = true;
                        }
                    }
                }
            }
        }
        /*
        //在A、D区
        if(longitude<=midLongitude){
            branchSquareRange.rightLongitude=midLongitude;
            if(latitude<=midLatitude){//A区
                branchSquareRange.topLatitude=midLatitude;
                indexBranch=wholeTree[indexBranch].childPointerList[0];
            }
            else{//D区
                branchSquareRange.downLatitude=midLatitude;
                indexBranch=wholeTree[indexBranch].childPointerList[3];
            }

        }
        else{//在B、C区
            branchSquareRange.leftLongitude=midLongitude;
            if(latitude<=midLatitude){//B区
                branchSquareRange.topLatitude=midLatitude;
                indexBranch=wholeTree[indexBranch].childPointerList[1];
            }
            else{//C区
                branchSquareRange.downLatitude=midLatitude;
                indexBranch=wholeTree[indexBranch].childPointerList[2];
            }
        }*/
        return _findPointInTree(wholeTree,indexBranch,branchSquareRange,longitude,latitude);
    }

    /*
     *在在Quad tree查找一个矩形区域所属叶节点列表
     *参数:
     *  1. whileTree：整棵树的mapping
     *  2. limitSquareRange: quad最大区域限制
     *  3. squareTarget:需要被查找的矩形区域
     *  4. resultList:保存目标矩形区域覆盖的叶节点在mapping类型的在Quad tree中的关键字的数组
    */
    function _findSquareInTree(mapping(uint256=>TreeNode) storage wholeTree,SquareRange memory limitSquareRange,
                                    SquareRange memory squareTarget, uint256[] storage resultList) public {
        //定义根节点在mapping token_Quad_tree中的关键字
        uint256 indexRoot=0;
        
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
     *在Quad tree查找一个矩形区域所属叶节点列表
     *参数:
     *  1. whileTree:整棵树的mapping
     *  2. indexBranch:待查找分支在whileTree中的根索引
     *  3. branchSquareRange:待查找分支的根表示的空间范围
     *  4. targetSquareRange:查询目标矩形的空间范围
     *  5. resultList:保存目标矩形区域覆盖的叶节点在mapping类型的Quad tree中的关键字的数组
    */
    function _findSquareInTree(mapping(uint256=>TreeNode) storage wholeTree,uint256 indexBranch,
                                   SquareRange memory branchSquareRange,SquareRange memory targetSquareRange,
                                   uint256[] storage resultList) public returns(bool completion){        
        //如果是叶节点,返回indexBranch
        if(wholeTree[indexBranch].childPointerList[0]==0){
            resultList.push(indexBranch);
            return true;
        }

        TreeNode storage branchRoot=wholeTree[indexBranch];
        SquareRange memory childrenSquareRange;
        uint256 nextIndexBranch;
        //依次处理四个子节点
        /*------- ---
         *| D  | C  |
         *|---------|
         *| A  | B  |
         *-----------
        */
        int256 midLongitude=(branchSquareRange.leftLongitude+branchSquareRange.rightLongitude)/2;
        int256 midLatitude=(branchSquareRange.downLatitude+branchSquareRange.topLatitude)/2;
        //A区
        childrenSquareRange.leftLongitude=branchSquareRange.leftLongitude;
        childrenSquareRange.rightLongitude=midLongitude;
        childrenSquareRange.downLatitude=branchSquareRange.downLatitude;
        childrenSquareRange.topLatitude=midLatitude;
        nextIndexBranch=branchRoot.childPointerList[0];

        if(isCovered(targetSquareRange,childrenSquareRange)){
            _findSquareInTree(wholeTree,nextIndexBranch,childrenSquareRange,targetSquareRange,resultList);
        }

        //B区
        childrenSquareRange.leftLongitude=midLongitude;
        childrenSquareRange.rightLongitude=branchSquareRange.rightLongitude;
        childrenSquareRange.downLatitude=branchSquareRange.downLatitude;
        childrenSquareRange.topLatitude=midLatitude;
        nextIndexBranch=branchRoot.childPointerList[1];

        if(isCovered(targetSquareRange,childrenSquareRange)){
            _findSquareInTree(wholeTree,nextIndexBranch,childrenSquareRange,targetSquareRange,resultList);
        }

        //C区
        childrenSquareRange.leftLongitude=midLongitude;
        childrenSquareRange.rightLongitude=branchSquareRange.rightLongitude;
        childrenSquareRange.downLatitude=midLatitude;
        childrenSquareRange.topLatitude=branchSquareRange.topLatitude;
        nextIndexBranch=branchRoot.childPointerList[2];

        if(isCovered(targetSquareRange,childrenSquareRange)){
            _findSquareInTree(wholeTree,nextIndexBranch,childrenSquareRange,targetSquareRange,resultList);
        }

        //D区
        childrenSquareRange.leftLongitude=branchSquareRange.leftLongitude;
        childrenSquareRange.rightLongitude=midLongitude;
        childrenSquareRange.downLatitude=midLatitude;
        childrenSquareRange.topLatitude=branchSquareRange.topLatitude;
        nextIndexBranch=branchRoot.childPointerList[3];

        if(isCovered(targetSquareRange,childrenSquareRange)){
            _findSquareInTree(wholeTree,nextIndexBranch,childrenSquareRange,targetSquareRange,resultList);
        }
    }

    /*
     *@dev 计算指定节点的区域范围
    */
    function calculateNodeRange(mapping(uint256=>TreeNode) storage wholeTree,SquareRange memory limitSquareRange,
                                uint256[] storage path) public view returns(SquareRange memory nodeRange){
        nodeRange=limitSquareRange;
        if(path.length==1||path.length==0)
            return nodeRange;
        for(uint256 i=0;i<path.length-1;i++){
            if(wholeTree[path[path.length-1-i]].childPointerList[0]==path[path.length-2-i]){
                nodeRange.rightLongitude=(nodeRange.leftLongitude+nodeRange.rightLongitude)/2; 
                nodeRange.topLatitude=(nodeRange.downLatitude+nodeRange.topLatitude)/2;       
            }
            if(wholeTree[path[path.length-1-i]].childPointerList[1]==path[path.length-2-i]){
                nodeRange.leftLongitude=(nodeRange.leftLongitude+nodeRange.rightLongitude)/2; 
                nodeRange.topLatitude=(nodeRange.downLatitude+nodeRange.topLatitude)/2;
            }
            if(wholeTree[path[path.length-1-i]].childPointerList[2]==path[path.length-2-i]){
               nodeRange.leftLongitude=(nodeRange.leftLongitude+nodeRange.rightLongitude)/2; 
               nodeRange.downLatitude=(nodeRange.downLatitude+nodeRange.topLatitude)/2;
            }
            if(wholeTree[path[path.length-1-i]].childPointerList[3]==path[path.length-2-i]){
               nodeRange.rightLongitude=(nodeRange.leftLongitude+nodeRange.rightLongitude)/2; 
               nodeRange.downLatitude=(nodeRange.downLatitude+nodeRange.topLatitude)/2; 
            }
        }
        return nodeRange;
    }

    /*
    *@dev 计算指定节点的路径
    * path: 存放计算结果
    */
    function nodePath(mapping(uint256=>TreeNode) storage wholeTree,uint256 indexNode,uint256[] storage path) public {
        if(indexNode==0)
            path.push(0);
        else{
            path.push(indexNode);
            nodePath(wholeTree,wholeTree[indexNode].parentPointer,path);
        }
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
    function isIncluded(SquareRange memory square,int256 longitude, int256 latitude) public pure returns(bool){
        if(longitude<square.leftLongitude||longitude>square.rightLongitude
            ||latitude<square.downLatitude||latitude>square.topLatitude)
            return false;
        return true;
    }
}