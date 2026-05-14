// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;

import "./Quad_tree.sol";
import "./ByteOperation.sol";
//无倒排文件
//contract DigitalAssetSharing is ERC721 {
contract QuadSubscriptionQuery {
    /**
    *定义元数据类型
    */

    struct Metadata{
        //数据产生时无人机位置--经度
        int256 longitude;
        //数据产生时无人机位置--纬度
        int256 latitude;
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
        Quad_tree.SquareRange geographicalRange;
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

    //记录queryID在_allQuerys中的位置，即索引
    mapping(uint256=>uint256) internal _allQuerysIndex;

    //query树节点映射
    mapping(uint256=>Quad_tree.TreeNode) internal _queryTree;
    //节点总数是产生下一个节点的标记，只增不减
    uint256 internal _sumQueryTreeNode;
    /* @dev query tree 中每个节点对应的queryID数组列表
     * uint256 表示节点在树中的索引
     * uint256[] 表示该节点中query的queryID数组，用每一个queryID去_queryCondition中找查询条件
    */
    mapping(uint256=>uint256[]) internal _queryIDList;

    uint8 internal _maxItemCount;//叶节点容量上限capacityLimit

    //订阅查询结果数组
    uint256[] internal _resultNodeList;
    uint256[] internal _resultQueryIDList;
    uint256[] internal _imposResultQueryIDList;

    //经纬度限制
    Quad_tree.SquareRange internal _limitSquareRange;

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
        _queryTree[0].childPointerList[0]=0;
        _sumQueryTreeNode=1;
        
        //指定叶节点附着query的最大个数
        _maxItemCount=10;

        //指定空间限制
        _limitSquareRange.leftLongitude=10000000000;
        _limitSquareRange.rightLongitude=800000000000;
        _limitSquareRange.downLatitude=10000000000;
        _limitSquareRange.topLatitude=800000000000;
    }

    //插入新订阅查询函数
    function insertNewSubscribeQuery(uint256 queryID, int256 leftlongitude, int256 rightlongitude,
                int256 downlatitude, int256 toplatitude, uint256 endtime, address owner,
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
        _allQuerysIndex[queryID]=_allQuerys.length-1;

        //将query插入queryTree
        _insertEntryInQueryTree(queryID);
    }

    //订阅查询
    function subscribeQuery(int256 longitude,int256 latitude,bytes[] memory keywords,
                    uint256 tokenID) external payable {
        Metadata memory resMetadata;
        resMetadata.longitude=longitude;
        resMetadata.latitude=latitude;
        resMetadata.keywords=keywords;

        uint256 indexNode=Quad_tree._findPointInTree(_queryTree,_limitSquareRange,longitude,latitude);
        
        bool isFind=false;

        //遍历叶节点上的query项
        for(uint8 j=0;j<_queryIDList[indexNode].length;j++){
            //判断token的位置是否落在query的范围内
            if(Quad_tree.isIncluded(_queryCondition[_queryIDList[indexNode][j]].geographicalRange,longitude,latitude)){
                //对比每一个查询关键词
                for(uint8 k=0;k<_queryCondition[_queryIDList[indexNode][j]].keywords.length;k++){
                    isFind=false;
                    for(uint8 l=0;l<keywords.length;l++){
                        if(ByteOperation.compare(_queryCondition[_queryIDList[indexNode][j]].keywords[k],keywords[l])){
                            isFind=true;
                            break;
                        }    
                    }
                    if(!isFind)
                        break;
                    if(k==_queryCondition[_queryIDList[indexNode][j]].keywords.length-1){
                        //queryID _queryIDList[indexNode][j]加入结果队列
                        _resultQueryIDList.push(_queryIDList[indexNode][j]);
                    }          
                }
            } 
        }
        
        emit SubResponse(tokenID, _resultQueryIDList);

        //清空查询结果数组
        ByteOperation.clearUint256List(_resultQueryIDList);
            
    }

    /*
     *@dev在query_tree插入query实体
     *2. 调用Quad_tree._splitNode()函数后,要重新指定分裂后的四个节点的queryIDList和倒排文件列表,
     *   要删除原节点的查询列表和倒排文件
     *3. 分裂条件：叶节点相关的query项超过_maxItemCount;
     *3. 调用成功后要增加树中总节点数,+4
    */
    function _insertEntryInQueryTree(uint256 queryID)private {
        QueryCondition memory query=_queryCondition[queryID];

        //调用检索函数NUP_tree._findSquareInTree,在queryTree上查找查询范围所在叶节点索引列表
        Quad_tree._findSquareInTree(_queryTree,_limitSquareRange,query.geographicalRange,_resultNodeList);
        
        Quad_tree.TreeNode storage targetNode;
        uint256 indexNode;

        //循环处理结果节点
        for(uint256 i=0;i<_resultNodeList.length;i++){
            indexNode=_resultNodeList[i];
            targetNode=_queryTree[indexNode];
            //向目标节点的_queryIDList添加指定的queryID
            _queryIDList[indexNode].push(queryID);

            split(indexNode);
        }
        //清空查询结果数组
        ByteOperation.clearUint256List(_resultNodeList);
    }

    function split(uint256 indexNode) internal {
        //检查叶节点的_queryIDList大小,确定是否达到分裂条件
        if(_queryIDList[indexNode].length>_maxItemCount){
            
            //先假设已经成功分裂了，处理分裂后的4个子节点上的查询附着关系，
            //之后如果没有达到使至少两个子节点的查询数量降低30%，就不执行分裂，并清空新增的queryIDList
            //查找indexNode的区域范围
            //_imposResultQueryIDList临时用来存放indexNode节点的路径
            Quad_tree.nodePath(_queryTree,indexNode,_imposResultQueryIDList);
            Quad_tree.SquareRange memory nodeRange;
            nodeRange=Quad_tree.calculateNodeRange(_queryTree,_limitSquareRange,_imposResultQueryIDList);
            ByteOperation.clearUint256List(_imposResultQueryIDList);

            //设置4个新的子节点的区域范围
            /*------- ---
            *| D  | C  |
            *|---------|
            *| A  | B  |
            *-----------
            */
            Quad_tree.SquareRange[4] memory childNodeRange;
            int256 midLongitude=(nodeRange.leftLongitude+nodeRange.rightLongitude)/2;
            int256 midLatitude=(nodeRange.downLatitude+nodeRange.topLatitude)/2;
            //子节点A
            childNodeRange[0].leftLongitude=nodeRange.leftLongitude;
            childNodeRange[0].rightLongitude=midLongitude;
            childNodeRange[0].downLatitude=nodeRange.downLatitude;
            childNodeRange[0].topLatitude=midLatitude;
            //子节点B
            childNodeRange[1].leftLongitude=midLongitude;
            childNodeRange[1].rightLongitude=nodeRange.rightLongitude;
            childNodeRange[1].downLatitude=nodeRange.downLatitude;
            childNodeRange[1].topLatitude=midLatitude;
            //子节点C
            childNodeRange[2].leftLongitude=midLongitude;
            childNodeRange[2].rightLongitude=nodeRange.rightLongitude;
            childNodeRange[2].downLatitude=midLatitude;
            childNodeRange[2].topLatitude=nodeRange.topLatitude;
            //子节点D
            childNodeRange[3].leftLongitude=nodeRange.leftLongitude;
            childNodeRange[3].rightLongitude=midLongitude;
            childNodeRange[3].downLatitude=midLatitude;
            childNodeRange[3].topLatitude=nodeRange.topLatitude;

            //处理子节点的_queryIDList项
            //逐个检查父节点上的query
            for(uint256 j=0;j<_queryIDList[indexNode].length;j++){
                //逐个子节点对比query是否与其重叠
                for(uint256 k=0;k<4;k++){
                    if(Quad_tree.isCovered(childNodeRange[k],
                    _queryCondition[_queryIDList[indexNode][j]].geographicalRange)){
                        _queryIDList[_sumQueryTreeNode+k].push(_queryIDList[indexNode][j]);
                    }
                }
            }
            //4个节点中有两个的quey项低于_maxItemCount*70%即可算成功分裂
            uint8 successNode=0;
            for(uint256 l=0;l<4;l++){
                if(_queryIDList[_sumQueryTreeNode+l].length<_maxItemCount*7/10)
                    successNode++;
            }
            if(successNode>1){
                //节点分裂
                Quad_tree._splitNode(_queryTree, indexNode, _sumQueryTreeNode);
                _sumQueryTreeNode+=4;
            }
            else{
                ByteOperation.clearUint256List(_queryIDList[_sumQueryTreeNode-4]);
                ByteOperation.clearUint256List(_queryIDList[_sumQueryTreeNode-3]);
                ByteOperation.clearUint256List(_queryIDList[_sumQueryTreeNode-2]);
                ByteOperation.clearUint256List(_queryIDList[_sumQueryTreeNode-1]);
            }       
        }
    }

    //维护订阅查询树--删除过期查询请求，只有当一个节点上没有任何query了，才可以删除节点
    function _deleteEntryInQueryTree(uint256 queryID)external {}


    /*测试_findPointInTree()的函数*/
    event NodeIN(uint256 indexNode);
    function findPointInTree(int256 longitude,int256 latitude)external returns(uint256 indexNode){
        indexNode=Quad_tree._findPointInTree(_queryTree,_limitSquareRange,longitude,latitude);
        emit NodeIN(indexNode);
        return indexNode;
    }
    /*测试_findSquareInTree()的函数*/
    event SquareCover(uint256[] indexNode);
    function findSquareCoverTree(int256 leftLongitude,int256 rightLongitude,int256 downLatitude,int256 topLatitude)
                external {
        Quad_tree.SquareRange memory targetSquareRange;
        targetSquareRange.leftLongitude=leftLongitude;
        targetSquareRange.rightLongitude=rightLongitude;
        targetSquareRange.downLatitude=downLatitude;
        targetSquareRange.topLatitude=topLatitude;
        Quad_tree._findSquareInTree(_queryTree,_limitSquareRange,targetSquareRange,_resultNodeList);
        emit SquareCover(_resultNodeList);
        //清空查询结果数组
        ByteOperation.clearUint256List(_resultNodeList);
    }

    /*
     * @dev 测试函数 返回指定的状态变量
    */
    function getAllQuerys()external view returns(uint256[] memory){
        return _allQuerys;
    }
    function getTheQueryCondition(uint256 queryID)external view returns(QueryCondition memory){
        return _queryCondition[queryID];
    }
    function getQueryIDList(uint256 queryTreeIndex)external view returns(uint256[] memory){
        return _queryIDList[queryTreeIndex];
    }

    function getSumQueryTreeNode()external view returns(uint256){
        return _sumQueryTreeNode;
    }
    function getTheQueryTreeNode(uint256 queryTreeNodeIndex)external view returns(Quad_tree.TreeNode memory){
        return _queryTree[queryTreeNodeIndex];
    }
}