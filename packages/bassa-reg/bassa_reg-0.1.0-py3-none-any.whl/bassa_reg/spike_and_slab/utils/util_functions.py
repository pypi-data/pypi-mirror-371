from datetime import datetime

import numpy as np


def get_date_for_experiment_name():
    return datetime.now().strftime("%Y_%m_%d-%H_%M_%S")

def calc_mse(y, y_hat):
    y = y.astype(np.float64).to_numpy()
    return np.mean((y - y_hat) ** 2)

def calc_mae(y, y_hat):
    y = y.astype(np.float64).to_numpy()
    return np.mean(np.abs(y - y_hat))

def calc_r2(y, y_hat):
    y = y.astype(np.float64).to_numpy()
    ss_res = np.sum((y - y_hat) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    return 1 - (ss_res / ss_tot)