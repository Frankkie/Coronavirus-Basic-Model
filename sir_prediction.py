""" Try to predict the spread of the Coronavirus.
    Perfect your model, collect data, or present your
    simulation in new ways."""

# Imports
import datetime
import time
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import worldometer_scrapping

# Global Variables
# Population of simulation
N = 6.4 * 10**9  # Here, it is the population of the entire planet, without China
# 15th of March
timestamp = 1585091136 - 10 * 24 * 3600  # 15th of March
T_START = datetime.date.fromtimestamp(timestamp)
""" Source of data: 
https://www.worldometers.info/coronavirus/coronavirus-cases/#case-distribution-outside-china"""
# For the 15th of March 2020, excluding mainland China
total_list = [88600]
new_cases_list = [1300]
deaths_list = [3300]
R_list = [13000]
I_list = [total_list[0] - R_list[0]]
S_list = [N - I_list[0] - R_list[0]]
date_list = [T_START]

death_rate = deaths_list[0] / R_list[0]

R0 = 2.55  # Basic Reproductive Rate
days_of_infectivity = 12
recovery_rate = 1 / days_of_infectivity
transmission_rate = R0 * recovery_rate

vaccine = False


def sir_method(b=transmission_rate, k=recovery_rate, duration=20):

    for j in range(duration):
        # Calculating the date i + 1 days after today
        date = datetime.date.fromtimestamp(timestamp + (j+1) * 24 * 3600)
        date_list.append(date)

        # Vaccination in day 500, all the population is vaccinated in a year
        if j > 500 and vaccine is True:
            S_list[-1] = S_list[-1] - S_list[490]/365
            if S_list[-1] < 0:
                S_list[-1] = 0

        S = S_list[-1]
        R = R_list[-1]
        I = I_list[-1]

        s = S_list[-1]/N
        r = R_list[-1]/N
        i = I_list[-1]/N

        ds_dt = -b*s*i
        dr_dt = k*i
        di_dt = -(ds_dt + dr_dt)

        rnew = int((dr_dt) * N)
        snew = int((ds_dt) * N)
        inew = int((di_dt) * N)

        R_list.append(R + rnew)
        S_list.append(S + snew)
        I_list.append(I + inew)
        total_list.append(total_list[-1] - snew)
        new_cases_list.append(-snew)
        deaths_list.append(deaths_list[-1] + int(death_rate * rnew))

        # Printing each days information
        print(str(date) + ": " + str(format(-snew, ',d')) + " new cases and "
              + str(format(total_list[-1], ',d')) + " total cases and "
              + str(format(deaths_list[-1], ',d')) + " deaths.")

    return


def plotting(dates, todays, cases, deaths):
    """ This function plots the number of new daily cases, total cases,
        and total deaths against time elapsed in the simulation, using
        matplotlib."""
    t = np.array(dates)
    c = np.array(cases)
    d = np.array(deaths)
    to = np.array(todays)

    fig, ax = plt.subplots()
    plt.yscale("linear")
    ax.plot(t, c)
    ax.plot(t, d)
    ax.plot(t, to)

    ax.set(xlabel='Days', ylabel='Cases',
           title='Flatten the curve, folks')
    ax.grid()

    # fig.savefig("test.png")
    plt.show()


sir_method()
plotting(date_list, new_cases_list, total_list, deaths_list)
