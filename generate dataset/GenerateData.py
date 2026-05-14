# 对2022年实验数据生成代码（GenerateData2022-1）的简化，实现的功能是一样的
import random
import numpy as np
import matplotlib.pyplot as plt  # 导入matplotlib模块，用于图表辅助分析
# %matplotlib inline
from pandas import DataFrame
import pandas as pd
from scipy import special

path_prefix = r'C:\WorkFile\3-实验室课题研究\研究-NFT辅助资源共享的无人机网络上的可验证查询\小论文扩展\实验数据\实验注入数据2'

def generateNormallyResource():
    # **************构造NFT数字资源元数据(正态分布)***************
    num = 2501 # 生成资源个数
    # 根据3 sigma(标准差) 法则，在99.7%的概率下在14-26之间，均值为20的服从正态分布的随机数，3sigma=(20-14)/3=2
    data_x = np.random.normal(20, 2, num)
    # 根据3 sigma 法则，均值为25的服从正态分布的随机数，22-28
    data_y = np.random.normal(25, 1, num)

    # 扩大1000，000，000倍，截取整数部分，再扩大10倍
    data_x = data_x * 1000000000
    data_x = np.ceil(data_x)
    data_x = data_x * 10
    data_y = data_y * 1000000000
    data_y = np.ceil(data_y)
    data_y = data_y * 10

    # 检查data_x和data_y中没有重复数值，集合（set）类型中的元素不重复
    if len(set(data_x)) == len(data_x):
        print('data_x has not same data!')
        if len(set(data_y)) == len(data_y):
            print('data_y has not same data!')
            timestamp = np.zeros((num,), dtype=int)
            timestamp += 1000
            keywordSet = ['0xaa', '0xbb']
            kws = []
            for i in range(0, num):
                sam_num = np.random.randint(1, 3) # 在[1,3)产生一个随机整数，即1或2
                kws.append(random.sample(keywordSet, sam_num)) # 在keywordSet随机取样，个数为sam_num

            # 将随机生成的num个数据写入Excel表格

            data = {'tokenID': range(0, num), 'Longitude': data_x, 'Latitude': data_y, 'timestamp': timestamp, 'keywords': kws}
            df = DataFrame(data)
            df.to_excel(r'{}\Normally_distribute_resource_data.xlsx'.format(path_prefix), index=False)

def generateUniformResource():
    # **************构造NFT数字资源元数据(均匀分布)***************
    num = 2501  # 生成资源个数
    #
    data_x = np.random.uniform(30000000000, 31000000000, num)

    data_y = np.random.uniform(20000000000, 21000000000, num)
    # 扩大10倍
    data_x = np.ceil(data_x)
    data_x = data_x * 10
    data_y = np.ceil(data_y)
    data_y = data_y * 10

    if len(set(data_x)) == len(data_x):
        print('data_x has not same data!')
        if len(set(data_y)) == len(data_y):
            print('data_y has not same data!')
            timestamp = np.zeros((num,), dtype=int)
            timestamp += 1000
            keywordSet = ['0xaa', '0xbb']
            kws = []
            for i in range(0, num):
                sam_num = np.random.randint(1, 3)
                kws.append(random.sample(keywordSet, sam_num))

            # 将随机生成的num个数据写入Excel表格
            data = {'tokenID': range(0, num), 'Longitude': data_x, 'Latitude': data_y, 'timestamp': timestamp, 'keywords': kws}
            df = DataFrame(data)
            df.to_excel(r'{}\Uniform_distribute_resource_data.xlsx'.format(path_prefix), index=False)

def zipfianRandom(constant=1.1, start=0, end=10000, part=50, size=2500):
    a = constant + 0.  # float类型，应该比1大
    # Samples are drawn from a Zipf distribution with specified parameter a > 1
    # s = np.random.zipf(a, 2000)
    # print(s)
    # count, bins, ignored = plt.hist(s[s < 100], 100, density=True)
    partion_number = part
    x = np.arange(1., partion_number + 1.)
    y = x ** (-a) / special.zetac(a)
    # print(x)
    # print(y)
    # plt.plot(x, y, linewidth=2, color='r')
    # plt.show()
    sum = 0.
    for num in range(0, partion_number):
        sum = sum + y[num]
    # print("sum", sum)
    size = size
    for num in range(0, partion_number):
        y[num] = ((size * 1.03) / sum * y[num])
    # print(y)
    print('Plan to sample', np.sum(y))
    # plt.plot(x, y, linewidth=2, color='r')
    # plt.show()

    sx = []
    sum = start
    rangenum = (end-start)/partion_number
    # print random.sample(list(np.arange(0, 700000)), int(y[0]))
    for num in range(0, partion_number):
        last = 1 + sum
        sum = sum + rangenum
        x = list(np.arange(last, sum))
        # append() 方法向列表的尾部添加一个新的元素。extend()方法只接受一个列表作为参数，并将该参数的每个元素都添加到原有的列表中。
        sx.extend(random.sample(x, int(y[num])))
    print('max(sx)', np.max(sx))
    print('min(sx)', np.min(sx))
    print('number of sx:', len(sx))
    # plt.hist(sx, 100)
    # plt.show()
    random.shuffle(sx)
    return sx[0:size]

def generateZipfianResource():
    # **************构造NFT数字资源元数据(长尾分布)***************
    num = 2500  # 生成资源个数
    #
    # data_x = np.random.uniform(30000000000, 31000000000, num)
    data_x = zipfianRandom(constant=2.0, start=3000000, end=3100000, part=50, size=num)
    print('max(data_x)', np.max(data_x))
    print('min(data_x)', np.min(data_x))
    print('number of data_x:', len(data_x))

    data_y = zipfianRandom(constant=2.0, start=2000000, end=2100000, part=50, size=num)
    print('max(data_y)', np.max(data_y))
    print('min(data_y)', np.min(data_y))
    print('number of data_y:', len(data_y))
    # 扩大100000倍
    data_x = np.ceil(data_x)
    data_x = data_x * 100000
    data_y = np.ceil(data_y)
    data_y = data_y * 100000
    plt.scatter(data_x,data_y)
    plt.show()

    if len(set(data_x)) == len(data_x):
        print('data_x has not same data!')
        if len(set(data_y)) == len(data_y):
            print('data_y has not same data!')
            timestamp = np.zeros((num,), dtype=int)
            timestamp += 1000
            keywordSet = ['0xaa', '0xbb']
            kws = []
            for i in range(0, num):
                sam_num = np.random.randint(1, 3)
                kws.append(random.sample(keywordSet, sam_num))

            # 将随机生成的num个数据写入Excel表格
            data = {'tokenID': range(0, num), 'Longitude': data_x, 'Latitude': data_y, 'timestamp': timestamp, 'keywords': kws}
            df = DataFrame(data)
            df.to_excel(r'{}\Zipfian_distribute_resource_data.xlsx'.format(path_prefix), index=False)

def generateQueryCondition(resource_file_path, query_file_path, queryNumber, resourceNumber):
    # **************构造查询条件数据***************
    # 从NFT数字资源元数据中均匀抽样num个，以该数据的坐标为中心，上下左右各扩展3个单位，成为一个查询范围条件
    queryNumber = queryNumber  # 生成资源个数
    resourceNumber = resourceNumber
    # 从磁盘读取NFT元数据excel
    metadata = pd.read_excel(resource_file_path, sheet_name='Sheet1')
    longitude = metadata['Longitude'][0:resourceNumber]
    latitude = metadata['Latitude'][0:resourceNumber]
    original_keywords = metadata['keywords'][0:resourceNumber]
    keywords = []

    # 修正keywords类型错误：从excel中读取keywords是str,但实际需要是list
    for i in range(0, len(original_keywords)):
        temp_keywords = original_keywords[i].replace('[', '')
        temp_keywords = temp_keywords.replace(']', '')
        temp_keywords = temp_keywords.replace('\'', '')
        temp_keywords = temp_keywords.replace(' ', '')
        temp_keywords = temp_keywords.split(sep=',')
        keywords.append(temp_keywords)

    # 在前resourceNumber个资源范围内随机生成queryNumber个均匀分布的整数
    randseq = np.random.randint(0,resourceNumber, queryNumber)  # <class 'numpy.ndarray'>
    leftLon = []
    rightLon = []
    bottomLat = []
    topLat = []
    queryKeywords =[]
    queryNo = []
    for i in range(0, len(randseq)):
        leftLon.append(longitude[randseq[i]]-3)
        rightLon.append(longitude[randseq[i]]+3)
        bottomLat.append(latitude[randseq[i]]-3)
        topLat.append(latitude[randseq[i]]+3)
        queryKeywords.append(keywords[randseq[i]])
        queryNo.append(i)

    # 查询条件存入excel
    data = {'leftLongitude': leftLon,
            'rightLongitude': rightLon,
            'bottomLatitude': bottomLat,
            'topLatitude': topLat,
            'queryKeywords': queryKeywords,
            'queryNo': queryNo}
    df = DataFrame(data)
    df.to_excel(query_file_path, index=False)

if __name__ == '__main__':
    ''''''
    # 生成正态分布数据和查询条件
    # generateNormallyResource()
    path_prefix = r'C:\WorkFile\5-毕业课题\单次查询实验\注入实验数据'
    resource_file_path = r'{}\Normally_distribute_resource_data.xlsx'.format(path_prefix)
    for round in range(0,25):
        resourceMaxNumber=(round+1)*20
        path_prefix = r'C:\WorkFile\5-毕业课题\单次查询实验\注入实验数据\无索引实验500以内查询条件'
        query_file_path = r'{0}\Normally_distribute_query_conditions_from{1}.xlsx'.format(path_prefix, resourceMaxNumber)
        # generateQueryCondition(resource_file_path, query_file_path, queryNumber=20, resourceNumber = resourceMaxNumber)

    # 生成均匀分布数据和查询条件
    # generateUniformResource()
    path_prefix = r'C:\WorkFile\5-毕业课题\单次查询实验\注入实验数据'
    resource_file_path = r'{}\Uniform_distribute_resource_data.xlsx'.format(path_prefix)
    for round in range(0,25):
        resourceMaxNumber=(round+1)*20
        path_prefix = r'C:\WorkFile\5-毕业课题\单次查询实验\注入实验数据\无索引实验500以内查询条件'
        query_file_path = r'{0}\Uniform_distribute_query_conditions_from{1}.xlsx'.format(path_prefix, resourceMaxNumber)
        generateQueryCondition(resource_file_path, query_file_path, queryNumber=20, resourceNumber = resourceMaxNumber)


    # 生成zipfian分布数据和查询条件
    # generateZipfianResource()
    resource_file_path = r'{}\Zipfian_distribute_resource_data.xlsx'.format(path_prefix)
    for round in range(0,5):
        resourceMaxNumber=(round+1)*500
        query_file_path = r'{0}\Zipfian_distribute_query_conditions_from{1}.xlsx'.format(path_prefix, resourceMaxNumber)
        # generateQueryCondition(resource_file_path, query_file_path, queryNumber=50, resourceNumber = resourceMaxNumber)

    # 从磁盘读取NFT元数据excel
    # file_path = r'C:\WorkFile\3-实验室课题研究\研究-NFT辅助资源共享的无人机网络上的可验证查询\实验数据\Normally_distribute_resource_data.xlsx'
    # metadata = pd.read_excel(file_path, sheet_name='Sheet1')
    
    

    # print(metadata.describe())
    '''
                 tokenID     Longitude      Latitude  timestamp
    count  100000.000000  1.000000e+05  1.000000e+05   100000.0
    mean    49999.500000  4.995876e+11  4.001268e+11     1000.0
    std     28867.657797  8.039563e+10  3.997395e+10        0.0
    min         0.000000  1.335829e+11  2.322546e+11     1000.0
    25%     24999.750000  4.453677e+11  3.731116e+11     1000.0
    50%     49999.500000  4.991047e+11  4.001391e+11     1000.0
    75%     74999.250000  5.541506e+11  4.268809e+11     1000.0
    max     99999.000000  8.257314e+11  5.711613e+11     1000.0
    

    longitude = metadata['Longitude']
    latitude = metadata['Latitude']
    print("max longitude: {}, min longitude: {}".format(max(longitude),min(longitude)))
    print("max latitude: {}, min latitude: {}".format(max(latitude),min(latitude)))
    longitude = np.random.lognormal(3, 1, 500)
    latitude = np.random.lognormal(2, 0.8, 1000)
    plt.scatter(longitude, latitude)
    plt.xlim(100000000000, 900000000000)
    plt.ylim(200000000000, 700000000000)
    plt.hist(longitude,100)
    print(longitude)
    plt.show()'''

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
    print(np.random.normal(10,0.3,(10,2)))
    print('-'*50)'''
    
    '''
    # 返回指定形状的标准正态分布数组
    data = np.random.standard_normal((10, 2))
    # 根据3 sigma 法则，在99.7%的概率下取50-100之间，均值为75的服从正太分布的随机数
    data = np.random.normal(75, 8.33, (100000, 2))
    data = data * 1000
    data = np.ceil(data)
    data = data * 1000
    data_x = data[:, 0]
    data_y = data[:, 1]
    

    # plt.scatter(longitude,latitude,s=3)
    # plt.show()'''
