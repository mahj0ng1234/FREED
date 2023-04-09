import numpy as np
import random
import time
from encryption import paillier
from model.opt import opt
from model_util import loadNetwork, extractFeatures, extractFeature, list_pictures
from secomp.secureprotol import SecureComputing

if __name__ == '__main__':

    model = loadNetwork(opt.weight)
    print('model loading success!')

    queryPath = 'D:\\python-workspace\\python-workspace\\datasets\\Market-1501\\query1'
    probe = list_pictures(queryPath)
    qf = extractFeatures(model, probe)
    galleryPath = 'D:\\python-workspace\\python-workspace\\datasets\Market-1501\\num_gallery\\gallery10'
    gallery = list_pictures(galleryPath)
    gf = extractFeatures(model, gallery)
    g_g_dist = np.dot(gf, np.transpose(gf))
    k = len(gallery) // 2
    g_dist_k = np.zeros(len(gallery))
    for i in range(len(gallery)):
        g_dist_k[i] = float(sorted(g_g_dist[i], reverse=True)[k:k+1][0])

    q_g_dist = np.dot(qf, np.transpose(gf))
    for j in range(len(qf)):
        initial_rank = np.argpartition(-q_g_dist[j], range(k))[:k]
        count = 0
        for index in initial_rank:
            if q_g_dist[j][index] >= g_dist_k[index]:
                count += 1
        if count >= k * 3 // 10:
            print(probe[j], count)
    """print('-----------')
    for j in range(len(qf)):
        initial_rank = np.argpartition(-q_g_dist[j], range(k))[:k]
        count = 0
        for index in initial_rank:
            g_g_dist[index][index] = q_g_dist[j][index]
            reciprocal_rank = np.argpartition(-g_g_dist[index], range(k))[:k]
            if index in reciprocal_rank:
                count += 1
        if count >= len(gf) // 2:
            print(probe[j], count)"""

    print('----------Encrypted version-----------')
    s=time.time()
    public_key, private_key, partial_private_keys = paillier.generate_paillier_keypair(n_length=256)
    # encrypt gallery
    gf_numpy = gf.numpy()
    enc_gf = np.zeros((len(gf_numpy),len(gf_numpy[0])), dtype=paillier.EncryptedNumber)
    for i in range(len(gf_numpy)):
        for j in range(len(gf_numpy[i])):
            enc_gf[i][j] = public_key.encrypt(gf_numpy[i][j].item())


    # encrypt the k-the of g_g_dist
    """enc_g_dist_k = np.zeros(len(g_dist_k), dtype=paillier.EncryptedNumber)
    for i in range(len(enc_g_dist_k)):
        enc_g_dist_k[i] = public_key.encrypt(g_dist_k[i])"""

    cp = paillier.ThresholdPaillier(public_key, partial_private_keys.sk1)
    csp = paillier.ThresholdPaillier(public_key, partial_private_keys.sk2)
    sc = SecureComputing(cp, csp)
    s=time.time()
    qf_numpy = qf.numpy()
    enc_qf = np.zeros((len(qf_numpy), len(qf_numpy[0])), dtype=paillier.EncryptedNumber)
    for i in range(len(qf_numpy)):
        for j in range(len(qf_numpy[i])):
            enc_qf[i][j] = public_key.encrypt(qf_numpy[i][j].item())
            #print(private_key.decrypt(enc_qf[i][j]), qf_numpy[i][j].item())

    enc_q_g_dist, q_g_dist1 = sc.sdot(enc_qf, enc_gf)



    for j in range(len(q_g_dist1)):
        initial_rank = np.argpartition(-q_g_dist1[j], range(k))[:k]
        count = 0
        for index in initial_rank:
            if q_g_dist1[j][index] >= g_dist_k[index] * 24.036 ** 43:
                count += 1
        if count >= k * 3 // 10:
            print(probe[j], count)

