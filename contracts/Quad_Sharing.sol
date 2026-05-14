// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;

//import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
//import "@nomiclabs/buidler/console.sol";
import "./Quad_tree.sol";
import "./ByteOperation.sol";

/**
 * @title SampleERC721
 * @dev Create a sample ERC721 standard token
 */
//contract DigitalAssetSharing is ERC721 {
contract QuadQuery {
    /**
    *定义元数据类型
    */
    //数字资产的类型
    enum AssetType{PICTURE, VIDEO}
   // enum Dimensionality{LONGITUDE, LATITUDE}

    struct Metadata{
        //数据产生时无人机位置--经度
        int256 longitude;

        //数据产生时无人机位置--纬度
        int256 latitude;

        //数据产生的时间     未考虑好时间单位和格式
        uint256 timestamp;

        //关键词
        bytes[] keywords;

        //owner
        address owner;

        //URI
        bytes URI;

        //数字资产的类型
        AssetType type_;
    }

    //查询请求结构体
    struct QueryCondition{
        //地理范围
        Quad_tree.SquareRange geographicalRange;

        //订阅查询结束时间
        bool isSubscription;
        uint256 timeEnd;

        //查询关键词
        bytes[] keywords;   
    }
   //queryTree 和tokenTree的 Inverted file table item
   struct InvertItem{
       bytes keyword;
       uint256[] itemList;
   }

    //tokenID到metadata的mapping
    mapping(uint256=>Metadata) internal _tokenMetadata;

    //所有tokens的list
    uint256[] internal _allTokens;

    //记录账户拥有的所有tokenID
    mapping(address=>uint256[]) internal _ownedTokens;

    //记录一个tokenID在 _ownedTokens中的位置，即索引
    mapping(uint256=>uint256) internal _ownedTokensIndex;

    //记录tokenID在_allTokens中的位置，即索引
    mapping(uint256=>uint256) internal _allTokensIndex;

    //token inverted file item结构体=Metadata结构体
    //Inverted file table=tokenID数组列表，用tokenID去_tokenMetadata中找元数据

    //token树节点映射
    mapping(uint256=>Quad_tree.TreeNode) internal _tokenTree;
    //节点总数是产生下一个节点的标记，只增不减
    uint256 internal _sumTokenTreeNode;
    uint8 internal _currentLayer;
    /* @dev token tree 中每个节点对应的tokenID数组列表
     * uint256 表示节点在树中的索引
     * uint256[] 表示该节点中token的tokenID数组，用每一个tokenID去_tokenMetadata中找元数据
    */
    mapping(uint256=>uint256[]) internal _tokenIDList;
    //token tree中节点到倒排文件的映射
    mapping(uint256=>InvertItem[]) internal _tokenInvertItemList;

    //订阅查询树节点映射:
    mapping(uint256=>Quad_tree.TreeNode) internal _queryTree;
    uint256 internal _sumQueryTreeNode;
    //queryID到QueryCondition的mapping
    mapping(uint256=>QueryCondition) internal _queryTable;
    /* @dev query tree 中每个节点对应的queryID数组列表
     * uint256 表示节点在树中的索引
     * uint256[] 表示该节点中query的queryID数组，用每一个queryID去_queryTable中找元数据
    */
    mapping(uint256=>uint256[]) internal _queryIDList;
    //query tree中节点到倒排文件的映射
    mapping(uint256=>InvertItem[]) internal _queryInvertItemList;

    uint8 internal _maxItemCount;

    //单次查询结果数组
    uint256[] internal _queryResultNodeList;
    uint256[] internal _queryResultTokenIDList;
    uint256[] internal _queryResultTempTokenIDList;

    //经纬度限制
    Quad_tree.SquareRange internal _limitSquareRange;

    /**
    *@dev 首次查询结果事件。在下列情况下触发：
    *     1.单次查询请求处理完毕。
    *     2.订阅查询请求的第一次查询处理完毕。
    * 实践应用中，第一个参数应该为bytes[] tokenURI，实验时为了简单起见，用uint256[] tokenID代替
    */
    event FirstResponse(uint256[] tokenID, uint256 queryID, address requester);

    /**
    *@dev 订阅查询结果事件。在下列情况下触发：
    *     1.订阅查询请求的第二次及以后返回结果。
    * 实践应用中，第一个参数应该为bytes tokenURI，实验时为了简单起见，用uint256 tokenID代替
    */
    event SubResponse(uint256 tokenID, uint256 queryID, address requester, uint256 lastTime);
    
    //构造函数
    //constructor() ERC721("DigitalAssetSharing", "DAS") {
    constructor(){
        //构造token_NUP_tree空树
        _tokenTree[0].parentPointer=0;
        _tokenTree[0].childPointerList[0]=0;
        _sumTokenTreeNode=1;

        //构造query_NUP_tree空树
        _queryTree[0].parentPointer=0;
        _queryTree[0].childPointerList[0]=0;
        _sumQueryTreeNode=1;
        
        //指定叶节点附着token的最大个数
        _maxItemCount=10;
        //指定空间限制
        /*正态
        _limitSquareRange.leftLongitude=100000000000;
        _limitSquareRange.rightLongitude=900000000000;
        _limitSquareRange.downLatitude=200000000000;
        _limitSquareRange.topLatitude=700000000000;*/
        /*均匀*/
        _limitSquareRange.leftLongitude=300000000000;
        _limitSquareRange.rightLongitude=310000000000;
        _limitSquareRange.downLatitude=200000000000;
        _limitSquareRange.topLatitude=210000000000;
    }

    //铸币函数
    function mint_(uint256 tokenID, 
                 int256 longitude, int256 latitude, uint256 timestamp, 
                 address owner, 
                 string memory URI, 
                 uint8 type_,
                 bytes[] memory keywords) external payable {
        
        //super._safeMint(owner, tokenID);

        Metadata memory metadata;//=Metadata(longitude, latitude, timestamp, keywords, owner, URI, tampType);
        metadata.longitude=longitude;
        metadata.latitude=latitude;
        metadata.timestamp=timestamp;
        metadata.owner=owner;
        metadata.URI=bytes(URI);
        metadata.keywords=keywords;
        if(type_==1)
           metadata.type_=AssetType.PICTURE;
        else
            metadata.type_=AssetType.VIDEO;

        //维护token相关的数据结构
        _tokenMetadata[tokenID]=metadata;
        _allTokens.push(tokenID);
        _ownedTokens[owner].push(tokenID);
        _ownedTokensIndex[tokenID]=_ownedTokens[owner].length-1;
        _allTokensIndex[tokenID]=_allTokens.length-1;

        //将token插入tokenTree
        _insertEntryInTokenTree(tokenID);
        //更新token-tree当前层数
        if(_currentLayer<_tokenTree[_sumTokenTreeNode-1].layer){
            _currentLayer=_tokenTree[_sumTokenTreeNode-1].layer;
        }
    }

    //单次查询函数
    //function onceQuery(QueryCondition memory query,uint256 queryID) external payable {
   function onceQuery(int256 leftLongitude,int256 rightLongitude,int256 downLatitude,int256 topLatitude,
                    bytes[] memory keywords,uint256 queryID,bool useInvert) external payable {
        QueryCondition memory query;
        query.geographicalRange.leftLongitude=leftLongitude;
        query.geographicalRange.rightLongitude=rightLongitude;
        query.geographicalRange.downLatitude=downLatitude;
        query.geographicalRange.topLatitude=topLatitude;
        query.keywords=keywords;
        query.isSubscription=false;
        query.timeEnd=0;

        Quad_tree._findSquareInTree(_tokenTree,_limitSquareRange,query.geographicalRange,_queryResultNodeList);
        
        bool isFind=false;

        //遍历_queryResultNodeList中的每一个叶节点
        for(uint256 i=0;i<_queryResultNodeList.length;i++){
            if(!useInvert){
                //遍历叶节点上的token项
                for(uint8 j=0;j<_tokenIDList[_queryResultNodeList[i]].length;j++){
                    //对比每一个查询关键词
                    for(uint8 k=0;k<query.keywords.length;k++){
                        isFind=false;
                        for(uint8 l=0;l<_tokenMetadata[_tokenIDList[_queryResultNodeList[i]][j]].keywords.length;l++){
                            if(ByteOperation.compare(query.keywords[k],_tokenMetadata[_tokenIDList[_queryResultNodeList[i]][j]].keywords[l])){
                                isFind=true;
                                break;
                            }    
                        }
                        if(!isFind)
                            break;
                        if(k==query.keywords.length-1){
                            //判断token的位置是否落在query的范围内
                            if(Quad_tree.isIncluded(query.geographicalRange,
                                        _tokenMetadata[_tokenIDList[_queryResultNodeList[i]][j]].longitude,
                                        _tokenMetadata[_tokenIDList[_queryResultNodeList[i]][j]].latitude)){
                                _queryResultTokenIDList.push(_tokenIDList[_queryResultNodeList[i]][j]); 
                            }
                        }          
                    }
                }
            }
            else{
                //利用倒排文件检查query中的keywords
                //对比每一个查询关键词
                for(uint8 k=0;k<query.keywords.length;k++){
                    isFind=false;
                    //用查询关键词与倒排文件的每一项keyword比较
                    for(uint8 l=0;l<_tokenInvertItemList[_queryResultNodeList[i]].length;l++){
                        if(ByteOperation.compare(query.keywords[k],_tokenInvertItemList[_queryResultNodeList[i]][l].keyword)){
                            isFind=true;
                            //将该条倒排文件的itemList加入结果,如果k=0,即比较的是query的第一个关键词，则itemList全加入_queryResultTempTokenIDList,否在二者取交集
                            if(k==0)
                                ByteOperation.unionOfUint256List(_queryResultTempTokenIDList,_tokenInvertItemList[_queryResultNodeList[i]][l].itemList);
                            else
                                ByteOperation.intersectOfUint256List(_queryResultTempTokenIDList,_tokenInvertItemList[_queryResultNodeList[i]][l].itemList);
                            if(_queryResultTempTokenIDList.length==0)
                                isFind=false;
                            break;
                        }
                        
                    }
                    if(!isFind){
                        //清空_queryResultTempTokenIDList
                        ByteOperation.clearUint256List(_queryResultTempTokenIDList);
                        break;
                    }
                }
                //判断_queryResultTempTokenIDList中的每一个token是否落在query的范围内
                uint8 m=0;//用于倒排文件辅助查找的循环控制变量
                while(m<_queryResultTempTokenIDList.length){
                    //判断token的位置是否落在query的范围内
                    if(Quad_tree.isIncluded(query.geographicalRange,
                                _tokenMetadata[_queryResultTempTokenIDList[m]].longitude,
                                _tokenMetadata[_queryResultTempTokenIDList[m]].latitude))
                        m++;
                    else
                        ByteOperation.deleteOneElementFromUint256List(_queryResultTempTokenIDList,m);
                }       
                //_queryResultTokenIDList与_queryResultTempTokenIDList取并集
                ByteOperation.unionOfUint256List(_queryResultTokenIDList,_queryResultTempTokenIDList);
                ByteOperation.clearUint256List(_queryResultTempTokenIDList);
            }
        }
        emit FirstResponse(_queryResultTokenIDList,queryID,msg.sender);

        //清空查询结果数组
        ByteOperation.clearUint256List(_queryResultNodeList);
        ByteOperation.clearUint256List(_queryResultTokenIDList);
        ByteOperation.clearUint256List(_queryResultTempTokenIDList);
        /*while(_queryResultNodeList.length!=0)
            _queryResultNodeList.pop();
        while(_queryResultTokenIDList.length!=0)
            _queryResultTokenIDList.pop();*/
        //清空_queryResultTempTokenIDList
    }

    //订阅查询
    function subscriptionQuery(uint256 tokenID) external payable {}

    /*
     *@dev在token_NUP_tree插入新token
     *1. 调用NUP_tree._splitNode()函数前,要自行验证分裂点是否在待分裂节点的区域边界内
     *2. 调用NUP_tree._splitNode()函数后,要自行指定分裂后的左节点和右节点的倒排文件列表,
     *   如果是下级分裂,要删除原节点的倒排文件
     *3. 调用成功后要增加树中总节点数,同级分裂+1,下级分裂+2
    */
    /*测试_findPointInTree()的函数*/
    event NodeIN(uint256 indexNode);
    function findPointInTree(int256 longitude,int256 latitude)external returns(uint256 indexNode){
        indexNode=Quad_tree._findPointInTree(_tokenTree,_limitSquareRange,longitude,latitude);
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
        Quad_tree._findSquareInTree(_tokenTree,_limitSquareRange,targetSquareRange,_queryResultNodeList);
        emit SquareCover(_queryResultNodeList);
        //清空查询结果数组
        ByteOperation.clearUint256List(_queryResultNodeList);
    }

    function _insertEntryInTokenTree(uint256 tokenID)private {
        Metadata memory metadata=_tokenMetadata[tokenID];
        int256 longitude=metadata.longitude;
        int256 latitude=metadata.latitude;
        
        //调用检索函数Quad_tree._findPointInTree,在tokenTree上查找"点"所在叶节点索引
        uint256 indexNode=Quad_tree._findPointInTree(_tokenTree,_limitSquareRange,longitude, latitude);
        
        //向目标节点的_tokenIDList添加指定的tokenID，
        _tokenIDList[indexNode].push(tokenID);
        /*向_tokenInvertItemList修改/添加该tokenID对应的倒排项
        _addTokenToInvertList(indexNode,tokenID);*/

        //分裂节点
        split(indexNode);
    }

    /*
     *@dev 节点递归分裂
    */
    function split(uint256 indexNode) internal returns (bool complete){
        //检查叶节点的_tokenIDList大小,确定分裂与否
        if(_tokenIDList[indexNode].length>_maxItemCount){
            Quad_tree._splitNode(_tokenTree, indexNode, _sumTokenTreeNode);
            _sumTokenTreeNode+=4;

            //查找targetNode的区域范围
            //_queryResultTempTokenIDList临时用来存放indexNode节点的路径
            Quad_tree.nodePath(_tokenTree,indexNode,_queryResultTempTokenIDList);
            Quad_tree.SquareRange memory nodeRange;
            nodeRange=Quad_tree.calculateNodeRange(_tokenTree,_limitSquareRange,_queryResultTempTokenIDList);
            ByteOperation.clearUint256List(_queryResultTempTokenIDList);

            //设置4个新的子节点的区域范围
            Quad_tree.SquareRange[4] memory childNodeRange;
            int256 midLongitude=(nodeRange.leftLongitude+nodeRange.rightLongitude)/2;
            int256 midLatitude=(nodeRange.downLatitude+nodeRange.topLatitude)/2;
            childNodeRange[0].leftLongitude=nodeRange.leftLongitude;
            childNodeRange[0].rightLongitude=midLongitude;
            childNodeRange[0].downLatitude=nodeRange.downLatitude;
            childNodeRange[0].topLatitude=midLatitude;
            childNodeRange[1].leftLongitude=midLongitude;
            childNodeRange[1].rightLongitude=nodeRange.rightLongitude;
            childNodeRange[1].downLatitude=nodeRange.downLatitude;
            childNodeRange[1].topLatitude=midLatitude;
            childNodeRange[2].leftLongitude=midLongitude;
            childNodeRange[2].rightLongitude=nodeRange.rightLongitude;
            childNodeRange[2].downLatitude=midLatitude;
            childNodeRange[2].topLatitude=nodeRange.topLatitude;
            childNodeRange[3].leftLongitude=nodeRange.leftLongitude;
            childNodeRange[3].rightLongitude=midLongitude;
            childNodeRange[3].downLatitude=midLatitude;
            childNodeRange[3].topLatitude=nodeRange.topLatitude;

            //处理节点的_tokenIDList项，这是4个新产生的节点
            //逐个检查父节点上的token
            for(uint256 i=0;i<_tokenIDList[indexNode].length;i++){
                //逐个子节点对比token是否落在其中
                for(uint256 j=0;j<4;j++){
                    if(Quad_tree.isIncluded(childNodeRange[j],
                    _tokenMetadata[_tokenIDList[indexNode][i]].longitude,_tokenMetadata[_tokenIDList[indexNode][i]].latitude)){
                        _tokenIDList[_sumTokenTreeNode-4+j].push(_tokenIDList[indexNode][i]);
                    }
                }
            }
            
            /*处理节点的_tokenInvertItemList项
            _updateTokenInvertItemList(_sumTokenTreeNode-4);
            _updateTokenInvertItemList(_sumTokenTreeNode-3);
            _updateTokenInvertItemList(_sumTokenTreeNode-2);
            _updateTokenInvertItemList(_sumTokenTreeNode-1);*/
            
        }
        else
            return true;
        /*检查否需要递归*/
        for(uint8 k=0;k<4;k++){
            if(_tokenIDList[_sumTokenTreeNode-4+k].length>_maxItemCount)
                split(_sumTokenTreeNode-4+k);
        }
    }

    //维护订阅查询树--插入新查询请求,SQT--Subscription Query Tree
    function _insertEntryInSQT(QueryCondition calldata query)private {}

    //维护订阅查询树--删除过期查询请求，只有当一个节点上没有任何query了，才可以删除节点
    function _deleteEntryInSQT(QueryCondition calldata query)private {}

    /*
     *@dev 对token_NUP_tree叶节点的倒排文件快速排序

    */
    function _quickSort(uint256[] storage arr, uint8 left, uint8 right, uint8 nodeLayer) internal {
        uint8 i = left;
        uint8 j = right;

        if (i == j) return;
        
        //按经度排序
        if(nodeLayer%2==0){
            int256 pivot=_tokenMetadata[arr[left + (right - left) / 2]].longitude;
            while (i <= j) {
                while (_tokenMetadata[arr[i]].longitude < pivot) i++;
                while (pivot < _tokenMetadata[arr[j]].longitude) j--;
                if (i <= j) {
                    (arr[i], arr[j]) = (arr[j], arr[i]);
                    i++;
                    if(j!=0)
                       j--;
                }
            }
        }
        else{//按纬度排序
            int256 pivot=_tokenMetadata[arr[left + (right - left) / 2]].latitude;
            while (i <= j) {
                while (_tokenMetadata[arr[i]].latitude < pivot) i++;
                while (pivot < _tokenMetadata[arr[j]].latitude) j--;
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

    //重新设置节点的_tokenInvertItemList项
    function _updateTokenInvertItemList(uint256 indexNode)  internal {
        //清空indexNode节点对应的InvertItem
        while(_tokenInvertItemList[indexNode].length!=0){
            _tokenInvertItemList[indexNode].pop();
        }
        for(uint256 i=0;i<_tokenIDList[indexNode].length;i++){
            _addTokenToInvertList(indexNode, _tokenIDList[indexNode][i]);
        }
    }

    //向_tokenInvertItemList中添加单个token元数据倒排文件
    function _addTokenToInvertList(uint256 indexNode, uint256 tokenID) internal{
        bool flag=false;
        for(uint i=0;i<_tokenMetadata[tokenID].keywords.length;i++){
            flag=false;
            for(uint j=0;j<_tokenInvertItemList[indexNode].length;j++){
                if(ByteOperation.compare(_tokenMetadata[tokenID].keywords[i],_tokenInvertItemList[indexNode][j].keyword)){
                    _tokenInvertItemList[indexNode][j].itemList.push(tokenID);
                    flag=true;
                    break;
                }        
            }
            if(flag==false){
                uint256[] memory newitemList=new uint256[](1);
                newitemList[0]=tokenID;
                InvertItem memory newtokenInvertItem=InvertItem(_tokenMetadata[tokenID].keywords[i],newitemList);
                _tokenInvertItemList[indexNode].push(newtokenInvertItem);
            }
        }
    }
    /*
     * @dev 测试函数 返回指定的状态变量
    */
    function getAllTokens()external view returns(uint256[] memory){
        return _allTokens;
    }
    function getTheTokenMetadata(uint256 tokenID)external view returns(Metadata memory){
        return _tokenMetadata[tokenID];
    }
    function getTokenIDList(uint256 tokenTreeIndex)external view returns(uint256[] memory){
        return _tokenIDList[tokenTreeIndex];
    }
    function getTokenInvertItemList(uint256 tokenTreeIndex)external view returns(InvertItem[] memory){
        return _tokenInvertItemList[tokenTreeIndex];
    }
    function getSumTokenTreeNode()external view returns(uint256){
        return _sumTokenTreeNode;
    }
    function getTheTokenTreeNode(uint256 tokenTreeNodeIndex)external view returns(Quad_tree.TreeNode memory){
        return _tokenTree[tokenTreeNodeIndex];
    }
    function getTokenTreeHigh() external view returns(uint8){
        return _currentLayer;
    }
}