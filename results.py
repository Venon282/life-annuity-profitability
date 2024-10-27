import numpy as np
from json_to_md import Convert

to_the_line = '  \n'

def Results(datas, results, inputs):
    res = {}

    # Inputs section
    res = Inputs(res, datas['Values']['Inputs'], inputs)

    # Uncertains values section
    res = Uncertains(res, results, datas['Values']['Uncertains stats'], datas['Values']['Uncertains'], inputs)

    # Globals values section
    res = Globals(res, datas['Values']['Globals'], inputs)

    return Convert(res)

def Inputs(res, datas, inputs):
    dic = {}

    # If the input is desire to be display, add it to the results
    for (dk, dv), (ik, iv) in zip(datas.items(), inputs.items()):
        if dv:
            dic[dk] = iv

    # If we have inputs content, add the inputs title
    if len(dic) >0:
        res['Inputs'] = dic

    return res

def Uncertains(result, results, datas, datas_bool, inputs):
    lifespans = {}
    report = {}

    # Add the desire user quantils
    for qt in datas['quantils']:
        lifespans[f'quantil_{qt}'] = np.quantile(results, qt)

    # Add the desire user means
    # todo: it's useless, delete this possibility
    for mean in datas['means']:
        from_, to_ = int(mean[0]*len(results)), int(mean[1]*len(results))
        lifespans[f'mean_{mean[0]}_{mean[1]}'] = np.mean(results[from_: to_])

    lifespans['All'] = results

    # For each uncertainty results desire, calculate them
    for key, value in lifespans.items():
        res = {}
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

    # Get the break even point if desire
    if datas['Break-even Point (years)']:
        dic['Break-even Point (years)'] = round((inputs['housing_value'] - inputs['bunch']) / (inputs['rent'] * 12),2) if inputs['rent'] > 0 else None

    # Get the different profitability chance set-up
    all_ =  res['Results']['All']
    for pc in datas['Profitability Chance (%)']:
        dic[f'Profitability Chance (>{pc}% of the housing value)'] = round(len(all_['Profit'][all_['Profit']>(inputs['housing_value']*pc)]) / inputs['num_simulations'] * 100,2)

    # If some values, add a title
    if len(dic) > 0:
        res['Globals'] = dic

    return res
