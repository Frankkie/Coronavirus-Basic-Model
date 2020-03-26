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
N = 11.08 * 10**6  # Here, it is the population of the entire planet
# Starting date of simulation
timestamp = 1585177536 - 61 * 24 * 3600  # 22nd of January
T_START = datetime.date.fromtimestamp(timestamp)
""" Source of data: https://www.worldometers.info/coronavirus/"""
# For the 24th of January 2020
""" Assuming an initial death rate of 16% as shown in studies from
    the epidemic, we can show that the actual cases in Wuhan on
    January 24th were four times more than the actual count. With
    this in mind, we can predict the spread of the disease, with 
    the lockdown that was enacted on the same day."""

total_list = [1200 * 4]
new_cases_list = [430 * 2]
deaths_list = [40]
R_list = [60 * 4]
I_list = [total_list[0] - R_list[0]]
S_list = [N - I_list[0] - R_list[0]]
date_list = [T_START]

capacity = 3000
death_rate_over_capacity = 0.16
death_rate_under_capacity = 0.02
hosp_rate = 0.2

R0 = 2.5  # Basic Reproductive Rate
days_of_infectivity = 12
recovery_rate = 1 / days_of_infectivity
transmission_rate = R0 * recovery_rate


def sir_method(b=transmission_rate, k=recovery_rate, duration=30):

    for j in range(duration):
        # Calculating the date i + 1 days after today
        date = datetime.date.fromtimestamp(timestamp + (j+1) * 24 * 3600)
        date_list.append(date)

        # Wuhan shutting down
        if j > 5:
            b -= 0.007
            if b < 0:
                b = 0.01

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

        need_hospital = I * hosp_rate
        out_of_hospital = need_hospital - capacity
        if out_of_hospital < 0:
            out_of_hospital = 0
        in_hospital = need_hospital - out_of_hospital

        death_rate = ((out_of_hospital / need_hospital
                       * death_rate_over_capacity)
                       + (in_hospital / need_hospital
                          * death_rate_under_capacity))
        print(out_of_hospital / need_hospital, death_rate)
        dnew = int(death_rate * rnew)

        R_list.append(R + rnew)
        S_list.append(S + snew)
        I_list.append(I + inew)
        total_list.append(total_list[-1] - snew)
        new_cases_list.append(-snew)
        deaths_list.append(deaths_list[-1] + dnew)

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
    plt.yscale("log")
    ax.plot(t, c)
    ax.plot(t, d)
    ax.plot(t, to)

    ax.set(xlabel='Days', ylabel='Cases',
           title='Wuhan, China')
    ax.grid()

    # fig.savefig("test.png")
    plt.show()


sir_method()
plotting(date_list, new_cases_list, total_list, deaths_list)
