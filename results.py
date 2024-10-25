import json
import numpy as np
from json_to_md import Convert

to_the_line = '  \n'

def Results(results, inputs):
    res = {}

    with open('config.json', 'r') as file:
        datas = json.load(file)



    res = Inputs(res, datas['Values']['Inputs'], inputs)
    # res = to_the_line

    res = Uncertains(res, results, datas['Values']['Uncertains stats'], datas['Values']['Uncertains'], inputs)

    res = Globals(res, datas['Values']['Globals'], inputs)
    # results_str += to_the_line
    print(Convert(res))
    return Convert(res)
# inputs={
#             "housing_value":self.housing_value,
#             "bunch":self.bunch,
#             "rent":self.rent,
#             "num_simulations":self.num_simulations,
#             "table_year":self.table_year,
#             "peoples":self.peoples
#         })
def Inputs(res, datas, inputs):
    dic = {}

    for (dk, dv), (ik, iv) in zip(datas.items(), inputs.items()):
        if dv:
            dic[dk] = iv
            # str_ += f'**{dk}:** {iv}{to_the_line}{to_the_line}'

    if len(dic) >0:
        # str_ = f'# Inputs{to_the_line}' + str_
        res['Inputs'] = dic


    return res

def Uncertains(result, results, datas, datas_bool, inputs):
    lifespans = {}
    report = {}
    # res['A year of rent']               = inputs['rent'] * 12



    for qt in datas['quantils']:
        lifespans[f'quantil_{qt}'] = np.quantile(results, qt)

    for mean in datas['means']:
        from_, to_ = int(mean[0]*len(results)), int(mean[1]*len(results))
        lifespans[f'mean_{mean[0]}_{mean[1]}'] = np.mean(results[from_: to_])

    lifespans['All'] = results

    for key, value in lifespans.items():
        res = {}
        print(value * (inputs['rent'] * 12))
        print(value)
        print(inputs['rent'])
        trc = value * (inputs['rent'] * 12)
        ti = trc + inputs['bunch']
        p = inputs['housing_value'] - ti
        pp = (p / ti) * 100
        sl = value

        if datas_bool['Total Rent Cost']:
            res['Total Rent Cost']             = np.round(trc, 2)
        if datas_bool['Total Rent Cost']:
            res['Total Investment']            = np.round(ti, 2)
        if datas_bool['Total Rent Cost']:
            res['Profit']                      = np.round(p, 2)
        if datas_bool['Total Rent Cost']:
            res['Profitability Percentage']    = np.round(pp, 2)
        if datas_bool['Total Rent Cost']:
            res['Simulated Lifespan in years'] = np.round(sl, 2)
        report[key] = res

    result['Results'] = report
    return result


def Globals(res, datas, inputs):
    dic = {}
    if datas['Break-even Point (years)']:
        dic['Break-even Point (years)'] = round((inputs['housing_value'] - inputs['bunch']) / (inputs['rent'] * 12),2) if inputs['rent'] > 0 else None

    all_ =  res['Results']['All']
    for pc in datas['Profitability Chance (%)']:
        dic[f'Profitability Chance (>{pc}% of the housing value)'] = round(len(all_['Profit'][all_['Profit']>(inputs['housing_value']*pc)]) / inputs['num_simulations'] * 100,2)

    if len(dic) > 0:
        res['Globals'] = dic

    return res
