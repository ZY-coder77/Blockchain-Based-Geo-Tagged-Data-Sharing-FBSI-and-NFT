# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
from web3 import Web3
import json
import contract5_abi  # IE-tree结构，单次查询，最大扇出数为7，单节点最大记录数为5，合约无倒排文件辅助查询
import contract6_abi
import time
import pandas as pd

# from pandas import DataFrame
# from openpyxl import load_workbook
import matplotlib.pyplot as plt

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    # 连接Ganache:
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
    # print(w3.isConnected())

    # 获取最新区块号（区块高度）
    print('blockNumber is: %d' % w3.eth.blockNumber)

    # 设置默认账户，就是发起交易的地址
    w3.eth.defaultAccount = w3.eth.accounts[5]
    file_path = r'C:\实验数据\Resource_number_on_leaf_node.xlsx'
    data = pd.read_excel(file_path, sheet_name='Sheet1')
    ''''''
    CAKE_BSC_ADDRESS = Web3.toChecksumAddress('0x30c58F5E82B99037e8f9153c218615eDB58b6b16')
    CAKE_BSC_ABI = json.loads(contract5_abi.abi)
    token_contract = w3.eth.contract(address=CAKE_BSC_ADDRESS, abi=CAKE_BSC_ABI)
    
    nodeCount = token_contract.functions.getSumTokenTreeNode().call()
    tokenCountList = []
    count = 0
    # 获取叶节点上附着token的数量
    for i in range(0, nodeCount):
        # 获取节点，此处node为元组tuple类型
        node = token_contract.functions.getTheTokenTreeNode(i).call()
        if node[1]==0: # node没有子节点，即为叶节点
            tokenCount = token_contract.functions.getTokenIDList(i).call()
            # 写叶节点上附着token的数量
            data.loc[count, 'ZipfianIETree'] = len(tokenCount)
            count += 1

    '''
    CAKE_BSC_ADDRESS = Web3.toChecksumAddress('0xa8E66dC74546ACed64435A89d71e0c638A87c5a0')
    CAKE_BSC_ABI = json.loads(contract5_abi.abi)
    token_contract = w3.eth.contract(address=CAKE_BSC_ADDRESS, abi=CAKE_BSC_ABI)

    nodeCount = token_contract.functions.getSumTokenTreeNode().call()
    tokenCountList = []

    count = 0
    # 获取叶节点上附着token的数量
    for i in range(0, nodeCount):
        # 获取节点，此处node为元组tuple类型
        node = token_contract.functions.getTheTokenTreeNode(i).call()
        if node[1] == 0:  # node没有子节点，即为叶节点
            tokenCount = token_contract.functions.getTokenIDList(i).call()
            # 写叶节点上附着token的数量
            data.loc[count, 'UniformIETree'] = len(tokenCount)
            count += 1
    '''
    '''
    CAKE_BSC_ADDRESS = Web3.toChecksumAddress('0x9702f6E05BE557c3F37b326c46B39c3ec96D5d79')
    CAKE_BSC_ABI = json.loads(contract6_abi.abi)
    token_contract = w3.eth.contract(address=CAKE_BSC_ADDRESS, abi=CAKE_BSC_ABI)

    nodeCount = token_contract.functions.getSumTokenTreeNode().call()
    tokenCountList = []

    count = 0
    # 获取叶节点上附着token的数量
    for i in range(0, nodeCount):
        # 获取节点，此处node为元组tuple类型
        node = token_contract.functions.getTheTokenTreeNode(i).call()
        if node[1]==[0,0,0,0]:  # node没有子节点，即为叶节点
            tokenCount = token_contract.functions.getTokenIDList(i).call()
            # 写叶节点上附着token的数量
            data.loc[count, 'ZipfianQuadTree'] = len(tokenCount)
            count += 1'''

    '''
    CAKE_BSC_ADDRESS = Web3.toChecksumAddress('0x35683EF858BaDDAEa48fc4ab13Aef265B91EBDe9')
    CAKE_BSC_ABI = json.loads(contract6_abi.abi)
    token_contract = w3.eth.contract(address=CAKE_BSC_ADDRESS, abi=CAKE_BSC_ABI)
    nodeCount = token_contract.functions.getSumTokenTreeNode().call()
    tokenCountList = []

    count = 0
    # 获取叶节点上附着token的数量
    for i in range(0, nodeCount):
        # 获取节点，此处node为元组tuple类型
        node = token_contract.functions.getTheTokenTreeNode(i).call()
        if node[1]==[0,0,0,0]:  # node没有子节点，即为叶节点
            tokenCount = token_contract.functions.getTokenIDList(i).call()
            # 写叶节点上附着token的数量
            data.loc[count, 'UniformQuadTree'] = len(tokenCount)
            count += 1
    '''
    '''
    CAKE_BSC_ADDRESS = Web3.toChecksumAddress('0xBbB699977F88FcD6bd6E3FD9DDF495b8254B5Bf1')
    CAKE_BSC_ABI = json.loads(contract6_abi.abi)
    token_contract = w3.eth.contract(address=CAKE_BSC_ADDRESS, abi=CAKE_BSC_ABI)

    nodeCount = token_contract.functions.getSumTokenTreeNode().call()
    tokenCountList = []

    count = 0
    # 获取叶节点上附着token的数量
    for i in range(0, nodeCount):
        # 获取节点，此处node为元组tuple类型
        node = token_contract.functions.getTheTokenTreeNode(i).call()
        if node[1] == [0, 0, 0, 0]:  # node没有子节点，即为叶节点
            tokenCount = token_contract.functions.getTokenIDList(i).call()
            # 写叶节点上附着token的数量
            data.loc[count, 'NormallyQuadTree-bigRange'] = len(tokenCount)
            count += 1'''
    pd.DataFrame(data).to_excel(file_path, index=False)