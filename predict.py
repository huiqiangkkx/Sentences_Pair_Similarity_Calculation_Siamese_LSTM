# -*- coding: utf-8 -*-
# @Author  : Junru_Lu
# @File    : predict.py
# @Software: PyCharm
# @Environment : Python 3.6+
# @Reference : https://github.com/likejazz/Siamese-LSTM

# 基础包
import pandas as pd
import keras
from gensim.models import KeyedVectors
from util import make_w2v_embeddings, split_and_zero_padding, ManDist

'''
本配置文件用于验证预训练好的孪生网络模型
'''

# ------------------预加载------------------ #

# 中英文训练选择，默认使用英文训练集
s = input("type cn or en:")
if s == 'cn':
    TEST_CSV = './data/quora_test_segmented.csv'
    flag = 'cn'
    embedding_path = 'CnCorpus-vectors-negative64.bin'
    embedding_dim = 64
    max_seq_length = 20
    savepath = './data/cn_SiameseLSTM.h5'
else:
    TEST_CSV = './data/quora_test.csv'
    flag = 'en'
    embedding_path = 'GoogleNews-vectors-negative300.bin'
    embedding_dim = 300
    max_seq_length = 10
    savepath = './data/en_SiameseLSTM.h5'

# 是否启用预训练的词向量，默认使用随机初始化的词向量
o = input("type yes or no for choosing pre-trained w2v or not:")
if o == 'yes':
    # 加载词向量
    print("Loading word2vec model(it may takes 2-3 mins) ...")
    embedding_dict = KeyedVectors.load_word2vec_format(embedding_path, binary=True)
else:
    embedding_dict = {}

# 读取并加载测试集
test_df = pd.read_csv(TEST_CSV)
for q in ['question1', 'question2']:
    test_df[q + '_n'] = test_df[q]

# 将测试集词向量化
test_df, embeddings = make_w2v_embeddings(flag, embedding_dict, test_df, embedding_dim=embedding_dim)

# 预处理
X_test = split_and_zero_padding(test_df, max_seq_length)
Y_test = test_df['is_duplicate'].values

# 确认数据准备完毕且正确
assert X_test['left'].shape == X_test['right'].shape
assert len(X_test['left']) == len(Y_test)

# 加载预训练好的模型
model = keras.models.load_model(savepath, custom_objects={"ManDist": ManDist})
model.summary()


# -----------------主函数----------------- #

if __name__ == '__main__':

    # 预测并评估准确率
    prediction = model.predict([X_test['left'], X_test['right']])
    print(prediction)
    prediction_list = prediction.tolist()
    accuracy = 0
    for i in range(len(prediction_list)):
        if prediction_list[i][0] < 0.5:
            predict_pro = 0
        else:
            predict_pro = 1
        if predict_pro == Y_test[i]:
            accuracy += 1
    print(accuracy / len(Y_test))
