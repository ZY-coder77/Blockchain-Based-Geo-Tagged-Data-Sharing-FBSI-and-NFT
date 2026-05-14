// SPDX-License-Identifier: GPL-3.0

//pragma solidity ^0.8.0;
pragma solidity >=0.7.0 <0.9.0;

library ByteOperation{
    /*
    * @dev 比较两个bytes是否相同
    */
    function compare(bytes memory A, bytes memory B) public pure returns(bool){
        if(A.length == B.length){
            for(uint i = 0;i<A.length;++i){
                if(A[i] != B[i])
                    return false;
            }
        }else{
            return false;
        }
        return true;
    }

    /*
    * @dev 从uint256[]中删除一个元素，其它元素前移
    * index的排序从0---List.length-1
    */
    function deleteOneElementFromUint256List(uint256[] storage List, uint8 index) public {
        require(0<=index&&index<List.length,"It doesn't have this element!");
        for(uint8 i=index;i<List.length-1;i++){
            List[i]=List[i+1];
        }
        List.pop();
    }

    /*
    * @dev 清空uint256[]
    */
    function clearUint64List(uint64[] storage List) public {
        while(List.length!=0)
           List.pop(); 
    }

    function clearUint256List(uint256[] storage List) public {
        while(List.length!=0)
           List.pop(); 
    }

    /*
    * @dev 两个uint256[]取交集,交集结果存放在ListA中
    */
    function intersectOfUint256List(uint256[] storage ListA,uint256[] memory ListB) public {
        uint8 i=0;
        bool isEqual=false;
        while(i<ListA.length){
            isEqual=false;
            for(uint8 j=0;j<ListB.length;j++){
                if(ListA[i]==ListB[j]){
                    i++;
                    isEqual=true;
                    break;
                }
            }
            if(!isEqual){
                deleteOneElementFromUint256List(ListA,i);
            }
        }
    }

    /*
    * @dev 两个uint256[]取并集，并集结果存放在ListA中
    */
    function unionOfUint256List(uint256[] storage ListA,uint256[] memory ListB) public{
        bool isEqual=false;
        uint8 oldListALength=uint8(ListA.length);
        for(uint8 i=0;i<ListB.length;i++){
            isEqual=false;
            for(uint8 j=0;j<oldListALength;j++){
                if(ListB[i]==ListA[j]){
                    isEqual=true;
                    break;
                }
            }
            if(!isEqual){
                ListA.push(ListB[i]);
            }
        }
    }

     /*
    * @dev 两个uint256[]取差集，ListA=ListA-ListB，差集结果存放在ListA中
    */
    function exceptOfUint256List(uint256[] storage ListA,uint256[] storage ListB) public{
        uint8 i=0;
        bool isEqual=false;
        while(i<ListA.length){
            isEqual=false;
            for(uint8 j=0;j<ListB.length;j++){
                if(ListA[i]==ListB[j]){
                    deleteOneElementFromUint256List(ListA,i);
                    isEqual=true;
                    break;
                }
            }
            if(!isEqual){
                i++;
            }
        }
    }

}