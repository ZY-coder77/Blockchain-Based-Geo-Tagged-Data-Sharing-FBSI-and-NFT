import random
import numpy as np
import matplotlib.pyplot as plt  # 导入matplotlib模块，用于图表辅助分析
# %matplotlib inline
from pandas import DataFrame
import pandas as pd

# 产生正态分布的订阅查询数据，对应的必中流数据和不中流数据
def generateNormallySubscriptionAndStream(subscriptionQuery_file_path, hitTokenStream_file_path, number=100):
    # **************构造订阅查询数据(正态分布)***************
    
    # 根据3 sigma 法则，均值为25的服从正态分布的随机浮点数，在99.7%的概率下在22-28之间，方差为1，3sigma=(25-22)/3=1
    # data_y = np.random.normal(25, 1, number)
    # 生成二维正太分布数据
    # 第一个参数：float类型，表示此正态分布的均值（对应整个分布中心）
    # 第二个参数：float类型，表示此正态分布的标准差（对应于分布的密度，scale越大越矮胖，数据越分散；scale越小越瘦高，数据越集中）
    # 第三个参数：输出的shape，size=(k,m,n) 表示输出k维，m行，n列的数，默认为None，只输出一个值，size(k,m)表示k个m维数
    # 根据3 sigma 法则，均值为50的服从正态分布的随机浮点数，在99.7%的概率下在20-80之间，方差为1，3sigma=(50-20)/3=10
    data = np.random.normal(50,10,(number,2))
    # 如果最大值超过80或最小值小于20，则重新取随机数
    
    while(np.max(data[:, 0])>80 or np.min(data[:, 0])<20 or np.max(data[:, 1])>80 or np.min(data[:, 1])<20):
        data = np.random.normal(50,10,(number,2))

    # 2n等于查询区域边长（正方形）
    data = data * 100000
    data = np.ceil(data)
    data = data * 100000 # 每个点上下左右间隔100000
    data_x = data[:, 0] # 订阅查询区域中心点x坐标
    data_y = data[:, 1] # 订阅查询区域中心点y坐标
    n = 100 # 查询区域边长200
    
    # 生成订阅查询数据
    leftLongitude = data_x - n
    rightLongitude = data_x + n
    downLatitude = data_y - n
    topLatitude = data_y + n
    endtime = np.zeros((number,), dtype=int)
    endtime += 1000
    keywordSet = ['0xaa', '0xbb']
    kws = []
    # 为每个查询随机选取关键字
    for i in range(0, number):
        kws.append(keywordSet)

    # 将随机生成的number个数据写入Excel表格
    data = {'queryID': range(0, number), 'leftLongitude': leftLongitude, 'rightLongitude': rightLongitude,
            'downLatitude': downLatitude, 'topLatitude': topLatitude, 'endtime': endtime, 'keywords': kws}
    df = DataFrame(data)
    df.to_excel(subscriptionQuery_file_path, index=False)

    # 生成必中数据流
    longitude = data_x
    latitude = data_y

    # 写入excel
    data = {'tokenID': range(0, number), 'longitude': longitude, 'latitude': latitude, 'keywords': kws}
    df = DataFrame(data)
    df.to_excel(hitTokenStream_file_path, index=False)


# 产生均匀分布的订阅查询数据，对应的必中流数据和不中流数据
def generateUniformSubscriptionAndStream(subscriptionQuery_file_path, hitTokenStream_file_path, number=100):
    # **************构造NFT数字资源元数据(均匀分布)***************
    # 在[1,80)随机生成number个2维均匀分布的浮点数
    data = np.random.uniform(1,80,(number,2))

    # 2n等于查询区域边长（正方形）
    data = data * 100000
    data = np.ceil(data)
    data = data * 100000 # 每个点上下左右间隔100000
    data_x = data[:, 0] # 订阅查询区域中心点x坐标
    data_y = data[:, 1] # 订阅查询区域中心点y坐标
    n = 100 # 查询区域边长200

    # 生成订阅查询数据
    leftLongitude = data_x - n
    rightLongitude = data_x + n
    downLatitude = data_y - n
    topLatitude = data_y + n
    endtime = np.zeros((number,), dtype=int)
    endtime += 1000
    keywordSet = ['0xaa', '0xbb']
    kws = []
    # 为每个查询随机选取关键字
    for i in range(0, number):
        # sam_num = np.random.randint(1, 3)
        # kws.append(random.sample(keywordSet, sam_num))
        kws.append(keywordSet)

    # 将随机生成的number个数据写入Excel表格
    data = {'queryID': range(0, number), 'leftLongitude': leftLongitude, 'rightLongitude': rightLongitude,
            'downLatitude': downLatitude, 'topLatitude': topLatitude, 'endtime': endtime, 'keywords': kws}
    df = DataFrame(data)
    df.to_excel(subscriptionQuery_file_path, index=False)

    # 生成必中数据流
    longitude = data_x
    latitude = data_y

    # 写入excel
    data = {'tokenID': range(0, number), 'longitude': longitude, 'latitude': latitude, 'keywords': kws}
    df = DataFrame(data)
    df.to_excel(hitTokenStream_file_path, index=False)


# 用不着了，功能被上面两个函数替代了
def generateAsset(Number, SubscriptionQuery_file_path,
                  TokenStream_file_path):

    # **************构造地理-文本数据流(来源于订阅查询数据)***************
    # 从订阅查询数据中均匀抽样Number个
    resourceNumber = Number
     # 从磁盘读取订阅查询数据excel
    file_path = SubscriptionQuery_file_path
    metadata = pd.read_excel(file_path, sheet_name='Sheet1')
    leftLongitude = metadata['leftLongitude']
    downLatitude = metadata['downLatitude']
    endtime = metadata['endtime']
    original_keywords = metadata['keywords']
    keywords = []

    # 修正keywords类型错误：从excel中读取keywords是str,但实际需要是list
    for i in range(0, len(original_keywords)):
        temp_keywords = original_keywords[i].replace('[', '')
        temp_keywords = temp_keywords.replace(']', '')
        temp_keywords = temp_keywords.replace('\'', '')
        temp_keywords = temp_keywords.replace(' ', '')
        temp_keywords = temp_keywords.split(sep=',')
        keywords.append(temp_keywords)

    longitude = []
    latitude = []
    tokenKeywords = []
    tokenID = range(0, resourceNumber)
    for i in range(0, resourceNumber):
        query_index = i % len(endtime)#len(endtime)就是订阅查询的总数，这里是循环取订阅查询
        rand = np.random.randint(1,100)# 从[1,100)随机取一个数
        # 用订阅查询的左下角坐标+随机值来生成一个位置-文本数据
        longitude.append(leftLongitude[query_index] + rand)
        latitude.append(downLatitude[query_index] + rand)
        tokenKeywords.append(keywords[query_index])

    # 地理-文本数据流存入excel
    data = {'longitude': longitude,
            'latitude': latitude,
            'tokenKeywords': tokenKeywords,
            'tokenID': tokenID}
    df = DataFrame(data)
    df.to_excel(TokenStream_file_path, index=False)

if __name__ == '__main__':
    ''''''
    number = 500
    path_prefix = r'C:\订阅查询实验注入数据-2023'
    Normal_subscriptionQuery_file_path=r'{}\Normal_SubscriptionQuery.xlsx'.format(path_prefix)
    Uniform_subscriptionQuery_file_path=r'{}\Uniform_SubscriptionQuery.xlsx'.format(path_prefix)

    Normal_hitTokenStream_file_path=r'{}\Normal_hitTokenStram.xlsx'.format(path_prefix)
    Uniform_hitTokenStream_file_path=r'{}\Uniform_hitTokenStram.xlsx'.format(path_prefix)

    generateNormallySubscriptionAndStream(Normal_subscriptionQuery_file_path, Normal_hitTokenStream_file_path, number)
    generateUniformSubscriptionAndStream(Uniform_subscriptionQuery_file_path, Uniform_hitTokenStream_file_path, number)




    ''''''
    # 从磁盘读取NFT元数据excel
    # file_path = r'C:\WorkFile\服务器实验数据\Uniform_distribute_resource_stream_{}.xlsx'.format(num)
    # metadata = pd.read_excel(file_path, sheet_name='Sheet1')

    # longitude = metadata['longitude']
    # latitude = metadata['latitude']
    # print("max longitude: {}, min longitude: {}".format(max(longitude),min(longitude)))
    # print("max latitude: {}, min latitude: {}".format(max(latitude),min(latitude)))
    # plt.scatter(longitude, latitude)
    # plt.show()
    
    '''
    # random.seed(1)
    # **************均匀分布***************
    # 在[1，2)随机生成一个均匀分布的浮点数
    print(np.random.uniform(1,2))
    print('-'*50)
    # 在[0,1)随机生成3个2维均匀分布的浮点数
    print(np.random.rand(3,2))
    print('-'*50)
    # 在[1,10)随机生成3个2维均匀分布的浮点数
    print(np.random.uniform(1,10,(3,2)))
    print('-'*50)
    # 在[1,10)随机生成3个2维均匀分布的整数
    print(np.random.randint(1,10,(3,2)))
    print('*'*50)
    '''
    # **************正态分布***************
    '''
    # 随机生成3个2维标准正态分布，浮点数
    print(np.random.randn(3,2))
    print('-'*50)
    # 第一个参数：float类型，表示此正态分布的均值（对应整个分布中心）
    # 第二个参数：float类型，表示此正态分布的标准差（对应于分布的密度，scale越大越矮胖，数据越分散；scale越小越瘦高，数据越集中）
    # 第三个参数：输出的shape，size=(k,m,n) 表示输出k维，m行，n列的数，默认为None，只输出一个值，size=100，表示输出100个值
    print(np.random.normal(10,5,(1000,2)))
    print('-'*50)
    '''
    '''
    # 返回指定形状的标准正态分布数组
    data = np.random.standard_normal((10, 2))
    # 根据3 sigma 法则，在99.7%的概率下取50-100之间，均值为60的服从正太分布的随机数
    data = np.random.normal(60, 13.33, (100000, 2))
    data = data * 1000
    data = np.ceil(data)
    data = data * 1000
    data_x = data[:, 0]
    data_y = data[:, 1]
    '''

    # plt.scatter(longitude,latitude,s=3)
    # plt.show()