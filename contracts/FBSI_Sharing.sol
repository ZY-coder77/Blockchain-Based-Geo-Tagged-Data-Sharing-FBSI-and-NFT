// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;

//import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
//import "@nomiclabs/buidler/console.sol";
import "./NUP_tree.sol";
import "./ByteOperation.sol";

/**
 * @title SampleERC721
 * @dev Create a sample ERC721 standard token
 */
//contract DigitalAssetSharing is ERC721 {
contract DigitalAssetSharing {
    /**
    *定义元数据类型
    */
    //数字资产的类型
    enum AssetType{PICTURE, VIDEO}
   // enum Dimensionality{LONGITUDE, LATITUDE}

    struct Metadata{
        //数据产生时无人机位置--经度
        int64 longitude;

        //数据产生时无人机位置--纬度
        int64 latitude;

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
        NUP_tree.SquareRange geographicalRange;

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

    //token inverted file item结构体=Metadata结构体
    //Inverted file table=tokenID数组列表，用tokenID去_tokenMetadata中找元数据

    //token树节点映射
    mapping(uint64=>NUP_tree.TreeNode) internal _tokenTree;
    //节点总数是产生下一个节点的标记，只增不减
    uint64 internal _sumTokenTreeNode;
    //测试层数的时候用
    uint8 internal _currentLayer;

    /* token tree 中每个节点对应的tokenID数组列表
     * uint64 表示节点在树中的索引
     * uint256[] 表示该节点中token的tokenID数组，用每一个tokenID去_tokenMetadata中找元数据
    */
    mapping(uint64=>uint256[]) internal _tokenIDList;
    //token tree中节点到倒排文件的映射
    mapping(uint64=>InvertItem[]) internal _tokenInvertItemList;


    //树的最大扇出fanout
    uint8 internal _maxChildCount;
    //叶节点容量上限capacityLimit
    uint16 internal _maxItemCount;

    //单次查询结果数组
    uint64[] internal _queryResultNodeList;
    uint256[] internal _queryResultTokenIDList;
    uint256[] internal _queryResultTempTokenIDList;

    //经纬度限制
    NUP_tree.SquareRange internal _limitSquareRange;

    /**
    *@dev 首次查询结果事件。在下列情况下触发：
    *     1.单次查询请求处理完毕。
    *     2.订阅查询请求的第一次查询处理完毕。
    * 实践应用中，第一个参数应该为bytes[] tokenURI，实验时为了简单起见，用uint256[] tokenID代替
    */
    event FirstResponse(uint256[] tokenID, uint256 queryID, address requester);

    
    //构造函数
    //constructor() ERC721("DigitalAssetSharing", "DAS") {
    constructor(){
        //构造token_NUP_tree空树
        _tokenTree[0].parentPointer=0;
        _sumTokenTreeNode=1;
        
        //指定树的最大扇出数
        _maxChildCount=7;
        //指定叶节点容量上限，当容量上限大于总token数使可作为无索引方案使用
        _maxItemCount=10;

        //指定空间限制
        _limitSquareRange.leftLongitude=-1800000000000;
        _limitSquareRange.rightLongitude=1800000000000;
        _limitSquareRange.downLatitude=-900000000000;
        _limitSquareRange.topLatitude=900000000000;
    }

    //铸币函数
    function mint_(uint256 tokenID, 
                 int64 longitude, int64 latitude, uint256 timestamp, 
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
        

        //将token插入tokenTree
        _insertEntryInTokenTree(tokenID);
        //更新token-tree当前层数
        if(_currentLayer<_tokenTree[_sumTokenTreeNode-1].layer){
            _currentLayer=_tokenTree[_sumTokenTreeNode-1].layer;
        }
    }

    /*
     *@dev 为某一token添加关键词
     
    function addKeyWord(uint256 tokenID,string calldata _keyword) external {
        bytes memory keyword=bytes(_keyword);
        _tokenMetadata[tokenID].keywords.push(keyword);
    }
    
    function addKeyWord(uint256 tokenID,bytes calldata _keyword) external {
        _tokenMetadata[tokenID].keywords.push(_keyword);
    }*/

    //单次查询函数
    //function onceQuery(QueryCondition memory query,uint256 queryID) external payable {
   function onceQuery(int64 leftLongitude,int64 rightLongitude,int64 downLatitude,int64 topLatitude,
                    bytes[] memory keywords,uint256 queryID,bool useInvert) external payable {
        QueryCondition memory query;
        query.geographicalRange.leftLongitude=leftLongitude;
        query.geographicalRange.rightLongitude=rightLongitude;
        query.geographicalRange.downLatitude=downLatitude;
        query.geographicalRange.topLatitude=topLatitude;
        query.keywords=keywords;
        query.isSubscription=false;
        query.timeEnd=0;

        NUP_tree._findSquareInTree(_tokenTree,_limitSquareRange,query.geographicalRange,_queryResultNodeList);
        
        bool isFind=false;

        //遍历_queryResultNodeList中的每一个叶节点
        for(uint64 i=0;i<_queryResultNodeList.length;i++){
            if(!useInvert){
                //遍历叶节点上的token项
                for(uint8 j=0;j<_tokenIDList[_queryResultNodeList[i]].length;j++){
                    //对比每一个查询关键词
                    uint8 k=0;
                    for(k;k<query.keywords.length;k++){
                        isFind=false;
                        for(uint8 l=0;l<_tokenMetadata[_tokenIDList[_queryResultNodeList[i]][j]].keywords.length;l++){
                            if(ByteOperation.compare(query.keywords[k],_tokenMetadata[_tokenIDList[_queryResultNodeList[i]][j]].keywords[l])){
                                isFind=true;
                                break;
                            }    
                        }
                        if(!isFind)
                            break;
                    }
                    //如果查询关键词全部匹配上，则核对token是否落入查询范围
                    if(k==query.keywords.length){
                        if(NUP_tree.isIncluded(query.geographicalRange,
                                    _tokenMetadata[_tokenIDList[_queryResultNodeList[i]][j]].longitude,
                                    _tokenMetadata[_tokenIDList[_queryResultNodeList[i]][j]].latitude)){
                            _queryResultTokenIDList.push(_tokenIDList[_queryResultNodeList[i]][j]); 
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
                            //将该条倒排文件的itemList加入结果,如果k=0,即比较的是query的第一个关键词，则itemList全加入_queryResultTempTokenIDList,否则二者取交集
                            if(k==0){
                                //ByteOperation.unionOfUint256List(_queryResultTempTokenIDList,_tokenInvertItemList[_queryResultNodeList[i]][l].itemList);
                                for(uint8 s=0;s<_tokenInvertItemList[_queryResultNodeList[i]][l].itemList.length;s++){
                                    _queryResultTempTokenIDList.push(_tokenInvertItemList[_queryResultNodeList[i]][l].itemList[s]);
                                }
                            }
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
                    if(NUP_tree.isIncluded(query.geographicalRange,
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
        ByteOperation.clearUint64List(_queryResultNodeList);
        ByteOperation.clearUint256List(_queryResultTokenIDList);
        ByteOperation.clearUint256List(_queryResultTempTokenIDList);
    }

    /*
     *@dev在_tokenTree插入新token
     *1. 调用NUP_tree._splitNode()函数前,要自行验证分裂点是否在待分裂节点的区域边界内
     *2. 调用NUP_tree._splitNode()函数后,要自行指定分裂后的左节点和右节点的倒排文件列表,
     *   如果是下级分裂,要删除原节点的倒排文件
     *3. 调用成功后要增加树中总节点数,同级分裂+1,下级分裂+2
    */
    function _insertEntryInTokenTree(uint256 tokenID)private {
        Metadata memory metadata=_tokenMetadata[tokenID];
        int64 longitude=metadata.longitude;
        int64 latitude=metadata.latitude;
        
        //调用检索函数NUP_tree._findPointInTree,在tokenTree上查找"点"所在叶节点索引
        uint64 indexNode=NUP_tree._findPointInTree(_tokenTree,_limitSquareRange,longitude, latitude);
        
        //向目标节点的_tokenIDList添加指定的tokenID，
        NUP_tree.TreeNode storage targetNode=_tokenTree[indexNode];
        _tokenIDList[indexNode].push(tokenID);
        /*向_tokenInvertItemList修改/添加该tokenID对应的倒排项
        _addTokenToInvertList(indexNode,tokenID);*/

        //检查叶节点的_tokenIDList大小,确定分裂与否
        if(_tokenIDList[indexNode].length>_maxItemCount){
            int64 splitPoint;
            
            //下级分裂:分裂节点为根节点或者其父节点的子节点数已超过上限
            if(targetNode.parentPointer==indexNode||_tokenTree[targetNode.parentPointer].childNodeList.length>=_maxChildCount){
                //下级分裂
                _quickSort(_tokenIDList[indexNode], 0, 
                        uint8(_tokenIDList[indexNode].length-1), targetNode.layer);
                //计算分区点splitPoint。targetNode.layer%2==0表示分裂坐标为经度
                if(targetNode.layer%2==0)
                    splitPoint =(_tokenMetadata[_tokenIDList[indexNode][(_tokenIDList[indexNode].length-1)/2]].longitude+
                        _tokenMetadata[_tokenIDList[indexNode][(_tokenIDList[indexNode].length-1)/2+1]].longitude)/2;
                else
                    splitPoint =(_tokenMetadata[_tokenIDList[indexNode][(_tokenIDList[indexNode].length-1)/2]].latitude+
                        _tokenMetadata[_tokenIDList[indexNode][(_tokenIDList[indexNode].length-1)/2+1]].latitude)/2; 
                
                NUP_tree._splitNode(_tokenTree, indexNode, splitPoint, NUP_tree.SplitType.CHILD,
                        _sumTokenTreeNode);
                _sumTokenTreeNode+=2;
                
                //处理节点的_tokenIDList项，这是两个新产生的节点
                //左节点
                for(uint8 i=0;i<=(_tokenIDList[indexNode].length-1)/2;i++){
                    _tokenIDList[_sumTokenTreeNode-2].push(_tokenIDList[indexNode][i]);
                }
                //右节点
                for(uint8 j=uint8((_tokenIDList[indexNode].length-1)/2+1);j<_tokenIDList[indexNode].length;j++){
                    _tokenIDList[_sumTokenTreeNode-1].push(_tokenIDList[indexNode][j]);
                }
                /*处理节点的_tokenInvertItemList项
                _updateTokenInvertItemList(_sumTokenTreeNode-2);
                _updateTokenInvertItemList(_sumTokenTreeNode-1);*/
            }
            else{//同级分裂意味着分区维度是分裂节点父节点的分区维度，(targetNode.layer-1)%2==0表示分裂坐标为经度
                _quickSort(_tokenIDList[indexNode], 0, 
                        uint8(_tokenIDList[indexNode].length-1), targetNode.layer-1);
                if((targetNode.layer-1)%2==0){
                    splitPoint =(_tokenMetadata[_tokenIDList[indexNode][(_tokenIDList[indexNode].length-1)/2]].longitude+
                        _tokenMetadata[_tokenIDList[indexNode][(_tokenIDList[indexNode].length-1)/2+1]].longitude)/2;
                }   
                else
                    splitPoint =(_tokenMetadata[_tokenIDList[indexNode][(_tokenIDList[indexNode].length-1)/2]].latitude+
                        _tokenMetadata[_tokenIDList[indexNode][(_tokenIDList[indexNode].length-1)/2+1]].latitude)/2;
                
                NUP_tree._splitNode(_tokenTree, indexNode, splitPoint, NUP_tree.SplitType.BROTHER,
                        _sumTokenTreeNode);
                
                _sumTokenTreeNode+=1;

                //处理节点的_tokenIDList项，左节点是旧的，右节点是新的
                //右节点
                for(uint8 j=uint8((_tokenIDList[indexNode].length-1)/2+1);j<_tokenIDList[indexNode].length;j++){
                    _tokenIDList[_sumTokenTreeNode-1].push(_tokenIDList[indexNode][j]);
                }
                //左节点
                for(uint8 i=0;i<_tokenIDList[indexNode].length-((_tokenIDList[indexNode].length-1)/2+1);i++){
                    _tokenIDList[indexNode].pop();
                }
                
                /*处理节点的_tokenInvertItemList项
                _updateTokenInvertItemList(_sumTokenTreeNode-1);
                _updateTokenInvertItemList(indexNode);*/
            }
        }
    }


    /*
     *@dev 对token_NUP_tree叶节点的倒排文件快速排序

    */
    function _quickSort(uint256[] storage arr, uint8 left, uint8 right, uint8 nodeLayer) internal {
        uint8 i = left;
        uint8 j = right;

        if (i >= j) return;
        
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
    function _updateTokenInvertItemList(uint64 indexNode)  internal {
        //清空indexNode节点对应的InvertItem
        while(_tokenInvertItemList[indexNode].length!=0){
            _tokenInvertItemList[indexNode].pop();
        }
        for(uint8 i=0;i<_tokenIDList[indexNode].length;i++){
            _addTokenToInvertList(indexNode, _tokenIDList[indexNode][i]);
        }
    }

    //向_tokenInvertItemList中添加单个token元数据倒排文件
    function _addTokenToInvertList(uint64 indexNode, uint256 tokenID) internal{
        bool flag=false;
        for(uint8 i=0;i<_tokenMetadata[tokenID].keywords.length;i++){
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

    /*测试_findPointInTree()的函数*/
    event NodeIN(uint64 indexNode);
    function findPointInTree(int64 longitude,int64 latitude)external returns(uint64 indexNode){
        indexNode=NUP_tree._findPointInTree(_tokenTree,_limitSquareRange,longitude,latitude);
        emit NodeIN(indexNode);
        return indexNode;
    }
    /*测试_findSquareInTree()的函数*/
    event SquareCover(uint64[] indexNode);
    function findSquareCoverTree(int64 leftLongitude,int64 rightLongitude,int64 downLatitude,int64 topLatitude)
                external {
        NUP_tree.SquareRange memory targetSquareRange;
        targetSquareRange.leftLongitude=leftLongitude;
        targetSquareRange.rightLongitude=rightLongitude;
        targetSquareRange.downLatitude=downLatitude;
        targetSquareRange.topLatitude=topLatitude;
        NUP_tree._findSquareInTree(_tokenTree,_limitSquareRange,targetSquareRange,_queryResultNodeList);
        emit SquareCover(_queryResultNodeList);
        //清空查询结果数组
        ByteOperation.clearUint64List(_queryResultNodeList);
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

    function getTokenIDList(uint64 tokenTreeIndex)external view returns(uint256[] memory){
        return _tokenIDList[tokenTreeIndex];
    }

    function getTokenInvertItemList(uint64 tokenTreeIndex)external view returns(InvertItem[] memory){
        return _tokenInvertItemList[tokenTreeIndex];
    }

    function getSumTokenTreeNode()external view returns(uint64){
        return _sumTokenTreeNode;
    }

    function getTheTokenTreeNode(uint64 tokenTreeNodeIndex)external view returns(NUP_tree.TreeNode memory){
        return _tokenTree[tokenTreeNodeIndex];
    }

    function getTokenTreeHigh() external view returns(uint8){
        return _currentLayer;
    }
}