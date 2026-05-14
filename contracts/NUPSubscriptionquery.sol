// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;

import "./NUP_tree.sol";
import "./ByteOperation.sol";
//无倒排文件
//contract DigitalAssetSharing is ERC721 {
contract NUPSubscriptionQuery {
    /**
    *定义元数据类型
    */

    struct Metadata{
        //数据产生时无人机位置--经度
        int64 longitude;
        //数据产生时无人机位置--纬度
        int64 latitude;
        //数据产生的时间     
        uint256 timestamp;
        //关键词
        bytes[] keywords;
        //owner
        address owner;
        //URI
        bytes URI;
    }

    //查询请求结构体
    struct QueryCondition{
        //地理范围
        NUP_tree.SquareRange geographicalRange;
        //订阅查询结束时间,用区块号表示
        uint256 endTime;
        //查询关键词
        bytes[] keywords;   
        //查询发起者
        address owner;
    }

    //queryID到QueryCondition的mapping
    mapping(uint256=>QueryCondition) internal _queryCondition;

    //所有query的list
    uint256[] internal _allQuerys;

    //query树节点映射
    mapping(uint64=>NUP_tree.TreeNode) internal _queryTree;
    //节点总数是产生下一个节点的标记，只增不减
    uint64 internal _sumQueryTreeNode;
    /* @dev query tree 中每个节点对应的queryID数组列表
     * uint16 表示节点在树中的索引
     * uint256[] 表示该节点中query的queryID数组，用每一个queryID去_queryCondition中找查询条件
    */
    mapping(uint64=>uint256[]) internal _queryIDList;
    /*query tree中节点到倒排文件的映射
    mapping(uint16=>InvertItem[]) internal _queryInvertItemList;*/

    uint8 internal _maxChildCount;//树的最大扇出fanout
    uint16 internal _maxItemCount;//叶节点容量上限capacityLimit

    //订阅查询结果数组
    uint64[] internal _resultNodeList;
    uint256[] internal _resultQueryIDList;
    //uint256[] internal _imposResultQueryIDList;

    //经纬度限制
    NUP_tree.SquareRange internal _limitSquareRange;

    /**
    *@dev 订阅查询结果事件。在下列情况下触发：
    *     1.订阅查询请求的第二次及以后返回结果。
    * 实践应用中，第一个参数应该为bytes tokenURI，实验时为了简单起见，用uint256 tokenID代替
    */
    event SubResponse(uint256 tokenID, uint256[] queryIDList);
    
    //构造函数
    constructor(){
        //构造query_NUP_tree空树
        _queryTree[0].parentPointer=0;
        _sumQueryTreeNode=1;
        
        //指定树的最大扇出数
        _maxChildCount=7;
        //指定叶节点容量上限，当容量上限大于总查询数时可作为无索引方案使用本合约
        _maxItemCount=10;
        //指定空间限制
        _limitSquareRange.leftLongitude=-1800000000000;
        _limitSquareRange.rightLongitude=1800000000000;
        _limitSquareRange.downLatitude=-900000000000;
        _limitSquareRange.topLatitude=900000000000;
    }

    //插入新订阅查询函数，相当于DigitalAssestSharing.sol的铸币函数_mint
    function insertNewSubscribeQuery(uint256 queryID, int64 leftlongitude, int64 rightlongitude,
                int64 downlatitude, int64 toplatitude, uint256 endtime, address owner,
                bytes[] memory keywords) external payable {

        QueryCondition memory querycondition;
        querycondition.geographicalRange.leftLongitude=leftlongitude;
        querycondition.geographicalRange.rightLongitude=rightlongitude;
        querycondition.geographicalRange.downLatitude=downlatitude;
        querycondition.geographicalRange.topLatitude=toplatitude;
        querycondition.endTime=endtime;
        querycondition.keywords=keywords;
        querycondition.owner=owner;

        //维护query相关的数据结构
        _queryCondition[queryID]=querycondition;
        _allQuerys.push(queryID);

        //将query插入queryTree
        _insertEntryInQueryTree(queryID);
    }

    //订阅查询
    function subscribeQuery(int64 longitude,int64 latitude,bytes[] memory keywords,
                    uint256 tokenID) external payable {
        Metadata memory resMetadata;
        resMetadata.longitude=longitude;
        resMetadata.latitude=latitude;
        resMetadata.keywords=keywords;

        uint64 indexNode=NUP_tree._findPointInTree(_queryTree,_limitSquareRange,longitude,latitude);
        
        bool isFind=false;
        
        //遍历叶节点上的query项
        for(uint8 j=0;j<_queryIDList[indexNode].length;j++){
            //判断token的位置是否落在query的范围内
            if(NUP_tree.isIncluded(_queryCondition[_queryIDList[indexNode][j]].geographicalRange,longitude,latitude)){
                //对比每一个查询关键词
                uint8 k=0;
                for(k;k<_queryCondition[_queryIDList[indexNode][j]].keywords.length;k++){
                    isFind=false;
                    for(uint8 l=0;l<keywords.length;l++){
                        if(ByteOperation.compare(_queryCondition[_queryIDList[indexNode][j]].keywords[k],keywords[l])){
                            isFind=true;
                            break;
                        }    
                    }
                    if(!isFind)
                        break;
                }
                if(k==_queryCondition[_queryIDList[indexNode][j]].keywords.length){
                        //queryID _queryIDList[indexNode][j]加入结果队列
                        _resultQueryIDList.push(_queryIDList[indexNode][j]);
                }
            } 
        }
        
        emit SubResponse(tokenID, _resultQueryIDList);

        //清空查询结果数组
        ByteOperation.clearUint256List(_resultQueryIDList);    
    }

    /*
     *@dev在query_NUP_tree插入query实体
     *1. 调用NUP_tree._splitNode()函数前,要自行验证分裂点是否在待分裂节点的区域边界内
     *2. 调用NUP_tree._splitNode()函数后,要自行指定分裂后的左节点和右节点的查询条件列表,
     *   如果是下级分裂,要删除原节点的查询列表
     *3. 分裂条件1，叶节点相关的query项超过_maxItemCount; 分裂条件2，分裂可使相关叶节点的query项低于maxItemCount的70%
     *3. 调用成功后要增加树中总节点数,同级分裂+1,下级分裂+2
    */
    function _insertEntryInQueryTree(uint256 queryID)private {
        QueryCondition memory query=_queryCondition[queryID];

        //调用检索函数NUP_tree._findPointInTree,在queryTree上查找查询范围所在叶节点索引列表
        NUP_tree._findSquareInTree(_queryTree,_limitSquareRange,query.geographicalRange,_resultNodeList);
        
        
        NUP_tree.TreeNode storage targetNode;
        uint64 indexNode;
        int64 splitPoint;
        uint8 referenceLayer;
        uint64 preorderNode;
        uint64 postorderNode;
        NUP_tree.SplitType splitType;

        //循环处理结果节点
        for(uint64 i=0;i<_resultNodeList.length;i++){
            indexNode=_resultNodeList[i];
            targetNode=_queryTree[indexNode];
            //向目标节点的_queryIDList添加指定的queryID
            _queryIDList[indexNode].push(queryID);

            //检查叶节点的_queryIDList大小,确定是否达到分裂条件1
            if(_queryIDList[indexNode].length>_maxItemCount){
                
                //下级分裂:分裂节点为根节点或者其父节点的子节点数已超过上限
                if(targetNode.parentPointer==indexNode||_queryTree[targetNode.parentPointer].childNodeList.length>=_maxChildCount){
                    referenceLayer=targetNode.layer;
                    splitType=NUP_tree.SplitType.CHILD;
                    preorderNode=_sumQueryTreeNode;
                    postorderNode=_sumQueryTreeNode+1;    
                }
                else{//同级分裂意味着分区维度是分裂节点父节点的分区维度，(targetNode.layer-1)%2==0表示分裂坐标为经度
                    referenceLayer=targetNode.layer-1;
                    splitType=NUP_tree.SplitType.BROTHER;
                    preorderNode=indexNode;
                    postorderNode=_sumQueryTreeNode;
                }
                _quickSort(_queryIDList[indexNode], 0, 
                            uint8(_queryIDList[indexNode].length-1), referenceLayer);
                
                splitPoint=calculateSplitPoint(indexNode,referenceLayer);
                
                //实施节点分裂
                NUP_tree._splitNode(_queryTree, indexNode, splitPoint, splitType, _sumQueryTreeNode);
                //修改节点总数
                if(splitType==NUP_tree.SplitType.CHILD)
                    _sumQueryTreeNode+=2;
                else 
                    _sumQueryTreeNode+=1;
                //处理分裂后的左（前）右（后）节点上的queryIDList
                processqueryIDList(indexNode,preorderNode,postorderNode,splitPoint,referenceLayer);
            }
        }
        //清空查询结果数组
        ByteOperation.clearUint64List(_resultNodeList);
    }

    /*
     *@dev 计算query_tree节点的分裂线
    */
    function calculateSplitPoint(uint64 indexNode,uint8 referenceLayer) internal view returns(int64 splitPoint){
    
        int64 preNum;//用于计算分裂点的第一个数据
        int64 postNum;//用于计算分裂点的第二个数据
        
        if(referenceLayer%2==0){//参考层为经度分裂层
            //实验中我们所有的查询范围都不重叠，所以可以在这样做，其余时候应参考NUPSubscription_2023
            preNum=_queryCondition[_queryIDList[indexNode][(_queryIDList[indexNode].length-1)/2]]
                    .geographicalRange.rightLongitude;
            postNum=_queryCondition[_queryIDList[indexNode][(_queryIDList[indexNode].length-1)/2+1]]
                        .geographicalRange.leftLongitude;     
        }
        else{//参考层为纬度分裂层

            preNum=_queryCondition[_queryIDList[indexNode][(_queryIDList[indexNode].length-1)/2]]
                        .geographicalRange.topLatitude;
            postNum=_queryCondition[_queryIDList[indexNode][(_queryIDList[indexNode].length-1)/2+1]]
                        .geographicalRange.downLatitude; 
        }
        splitPoint =(preNum+postNum)/2;
    }

    /*
     *@dev 分裂后，处理子节点上的queryIDList
    */
    function processqueryIDList(uint64 indexNode,uint64 preorderNode,uint64 postorderNode,
                                int64 splitPoint,uint8 referenceLayer) internal {

        uint length = _queryIDList[indexNode].length;
        //选处理后续节点的_queryIDList，前一半查询是否覆盖后续节点
        for(uint16 j=0;j<(length-1)/2+1;j++){
            
            //参考层为经度层
            if(referenceLayer%2==0){ 
                //将右经度超过分裂点的查询添加到后序子节点上
                if(_queryCondition[_queryIDList[indexNode][j]].geographicalRange.rightLongitude>splitPoint)
                    _queryIDList[postorderNode].push(_queryIDList[indexNode][j]);
            }
            else{//参考层为纬度层
                if(_queryCondition[_queryIDList[indexNode][j]].geographicalRange.topLatitude>splitPoint)
                    _queryIDList[postorderNode].push(_queryIDList[indexNode][j]);
            }
        }
        //处理后一半query
        for(uint j=(length-1)/2+1;j<length;j++){
            _queryIDList[postorderNode].push(_queryIDList[indexNode][j]);
        }

        //如果是同级分裂，前序节点的后一半删除
        if(indexNode==preorderNode){
            for(uint j=(length-1)/2+1;j<length;j++){
                _queryIDList[indexNode].pop();
            }
        }
        else{//下级分裂则将前一半数据复制到前序节点
            for(uint8 j=0;j<(length-1)/2+1;j++){
                _queryIDList[preorderNode].push(_queryIDList[indexNode][j]);
            }
        }
    }

    //维护订阅查询树--删除过期查询请求，只有当一个节点上没有任何query了，才可以删除节点
    function _deleteEntryInQueryTree(uint256 queryID)external {}

    /*
     *@dev 对query_NUP_tree叶节点的_queryIDList快速排序
     *按照left longitude或down latitude排序
    */
    function _quickSort(uint256[] storage arr, uint8 left, uint8 right, uint8 nodeLayer) internal {
        uint8 i = left;
        uint8 j = right;

        if (i == j) return;
        
        //按经度排序
        if(nodeLayer%2==0){
            int256 pivot=_queryCondition[arr[left + (right - left) / 2]].geographicalRange.leftLongitude;
            while (i <= j) {
                while (_queryCondition[arr[i]].geographicalRange.leftLongitude < pivot) i++;
                while (pivot < _queryCondition[arr[j]].geographicalRange.leftLongitude) j--;
                if (i <= j) {
                    (arr[i], arr[j]) = (arr[j], arr[i]);
                    i++;
                    if(j!=0)
                       j--;
                }
            }
        }
        else{//按纬度排序
            int256 pivot=_queryCondition[arr[left + (right - left) / 2]].geographicalRange.downLatitude;
            while (i <= j) {
                while (_queryCondition[arr[i]].geographicalRange.downLatitude < pivot) i++;
                while (pivot < _queryCondition[arr[j]].geographicalRange.downLatitude) j--;
                if (i <= j) {
                    (arr[i], arr[j]) = (arr[j], arr[i]);
                    i++;
                    if(j!=0)
                        j--;
                }
            }
        }

        //递归        
        if (left < j)
            _quickSort(arr, left, j, nodeLayer);
        if (i < right)
            _quickSort(arr, i, right, nodeLayer);
    }


    /*测试_findPointInTree()的函数
    event NodeIN(uint64 indexNode);
    function findPointInTree(int64 longitude,int64 latitude)external returns(uint64 indexNode){
        indexNode=NUP_tree._findPointInTree(_queryTree,_limitSquareRange,longitude,latitude);
        emit NodeIN(indexNode);
        return indexNode;
    }*/
    /*测试_findSquareInTree()的函数
    event SquareCover(uint64[] indexNode);
    function findSquareCoverTree(int64 leftLongitude,int64 rightLongitude,int64 downLatitude,int64 topLatitude)
                external {
        NUP_tree.SquareRange memory targetSquareRange;
        targetSquareRange.leftLongitude=leftLongitude;
        targetSquareRange.rightLongitude=rightLongitude;
        targetSquareRange.downLatitude=downLatitude;
        targetSquareRange.topLatitude=topLatitude;
        NUP_tree._findSquareInTree(_queryTree,_limitSquareRange,targetSquareRange,_resultNodeList);
        emit SquareCover(_resultNodeList);
        //清空查询结果数组
        ByteOperation.clearUint64List(_resultNodeList);
    }*/

    /*
     * @dev 测试函数 返回指定的状态变量
    */
    function getAllQuerys()external view returns(uint256[] memory){
        return _allQuerys;
    }
    function getTheQueryCondition(uint256 queryID)external view returns(QueryCondition memory){
        return _queryCondition[queryID];
    }
    function getQueryIDList(uint64 queryTreeIndex)external view returns(uint256[] memory){
        return _queryIDList[queryTreeIndex];
    }
 
    function getSumQueryTreeNode()external view returns(uint64){
        return _sumQueryTreeNode;
    }
    function getTheQueryTreeNode(uint64 queryTreeNodeIndex)external view returns(NUP_tree.TreeNode memory){
        return _queryTree[queryTreeNodeIndex];
    }
}