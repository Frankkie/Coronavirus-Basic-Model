""" Try to predict the spread of the Coronavirus.
    Perfect your model, collect data, or present your
    simulation in new ways."""

# Imports
import datetime
import matplotlib.pyplot as plt
import numpy as np

import worldometer_scrapping

# Global variables
R0 = 2.45  # Basic Reproductive Rate, number of transmissions/infected person in a 100% susceptible population.
days_of_infectivity = 10  # period during which the infected remain infectious
recovery_rate = 1 / days_of_infectivity
transmission_rate = R0 * recovery_rate  # Number of transmissions per infected person per day


def init_data(scenario="world"):
    """ This function initializes the data the model needs depending on the scenario.
        Arguments:
            -scenario (keyword str): the scope that the model considers. Besides single countries, there is also
                                    "world", and "without China".
        Output:
            -data (dict): the data corresponding to the scenario. The structure of the dictionary is as follows:
            {"N": n, "T start": timestamp_start, "Total list": total_list, "Deaths list": deaths_list,
            "R list": R_list, "I list": I_list, "S list": S_list, "New cases list": new_cases_list,
            "Date list": date_list, "Death rate": death_rate}
            where:
                ~ N is the population of the scenario
                ~ T start is the timestamp of the starting date
                ~ Total list, the list that contains total confirmed cases day by day.
                ~ Deaths list, the list of total deaths day by day.
                ~ R list, contains the total non-active (removed/recovered) cases day by day.
                ~ I list, contains the total active cases (infected/infectious) day by day.
                ~ S list, contains the susceptible population numbers (not infected, not removed).
                ~ New cases list, contains the new infectious cases on each day.
                ~ Date list: the timestamps of the dates in the simulation.
                ~ Death rate: the percentage of new removed cases that are deaths, day by day.
                """

    # 22nd of January is the starting date
    timestamp_start = 1579651200

    if scenario == "without China":
        # If the scenario is the world, excluding mainland China, first retrieve world data
        # Later subtract the numbers from China.
        data = worldometer_scrapping.mine_data(scope="world")
    else:
        data = worldometer_scrapping.mine_data(scope=scenario)

    # Population of simulation
    n = data["demographics"]["population"]

    total_list = data["cases"]  # The list that contains total confirmed cases day by day.
    deaths_list = data["deaths"]  # The list of total deaths day by day.
    R_list = data["recovered"]  # Contains the total non-active (removed/recovered) cases day by day.
    I_list = data["active"]  # Contains the total active cases (infected/infectious) day by day.
    S_list = []  # Contains the susceptible population numbers (not infected, not removed).
    for i, val in enumerate(total_list):
        S_list.append(n - val)  # Total pop minus total confirmed cases

    new_cases_list = []  # Contains the new infectious cases on each day.
    date_list = []  # The timestamps of the dates in the simulation.
    death_rate = []  # The percentage of new removed cases that are deaths, day by day.
    for i, val in enumerate(total_list):
        if i == 0:
            new_cases_list.append(val)
        else:
            new_cases_list.append(val - total_list[i - 1])
        date_list.append(timestamp_start + i * 24 * 3600)
        rate = deaths_list[i] / (R_list[i] + 1)
        death_rate.append(rate)

    if scenario == "without China":
        # Subtract Chinese data off the world data.
        data_ = worldometer_scrapping.mine_data(scope="China")
        n -= data_["demographics"]["population"]
        for i, val in enumerate(total_list):
            total_list[i] = val - data_["cases"][i]
        for i, val in enumerate(deaths_list):
            deaths_list[i] = val - data_["deaths"][i]
        for i, val in enumerate(R_list):
            R_list[i] = val - data_["recovered"][i]
        for i, val in enumerate(I_list):
            I_list[i] = val - data_["active"][i]

        S_list = []
        for i, val in enumerate(total_list):
            S_list.append(n - val)

        new_cases_list = []
        death_rate = []
        for i, val in enumerate(total_list):
            if i == 0:
                new_cases_list.append(val)
            else:
                new_cases_list.append(val - total_list[i - 1])
            rate = deaths_list[i] / (R_list[i] + 1)
            death_rate.append(rate)

    data = {"N": n, "T start": timestamp_start, "Total list": total_list, "Deaths list": deaths_list,
            "R list": R_list, "I list": I_list, "S list": S_list, "New cases list": new_cases_list,
            "Date list": date_list, "Death rate": death_rate}
    return data


def sir_method(data, b=transmission_rate, k=recovery_rate, offset=0, run=90):
    """ This function implements the SIR model of infectious disease.
        S stands for Susceptible (the percentage of the population that can potentially get infected). With the novel
        coronavirus this percentage is 100%.
        R stands for Removed/Recovered (the cases that have recovered or have died and are no longer susceptible)
        I stands for Infected/Infectious (the number of people that carry the disease at any point in time, and can
        transmit it to others.
        Arguments:
            -data (dict): the data provided by the init_data function.
            -b (keyword, float): the rate of new infections per infectious person per day.
            -k (keyword, float): the percentage of infected people recovering/dying per day.
            -offset (keyword, int): Amount of days the model trims from the end of the data.
            -run (keyword, int): Amount of days after the offset date that the model runs for.
    """

    N = data["N"]  # Population of scenario
    # "Extracting" the lists from the data dictionary
    date_list = data["Date list"][:-offset]  # Dates as timestamps
    S_list = data["S list"][:-offset]  # Susceptible people
    R_list = data["R list"][:-offset]  # Removed cases
    I_list = data["I list"][:-offset]  # Infectious cases
    total_list = data["Total list"][:-offset]  # Total reported cases
    new_cases_list = data["New cases list"][:-offset]  # New cases every day
    deaths_list = data["Deaths list"][:-offset]
    death_rate = data["Death rate"][:-offset]  # Death rate defined as deaths in a day / removed in a day

    for j in range(run):
        # Calculating the next day timestamp
        date = date_list[-1] + 24 * 3600
        date_list.append(date)

        # Last day's SIR values
        S = S_list[-1]
        R = R_list[-1]
        I = I_list[-1]

        # SIR values as a percentage of the initial population
        s = S/N
        r = R/N
        i = I/N

        # The SIR differential equations
        ds_dt = -b*s*i  # Change in susceptible population in a day, as a percentage of initial population
        dr_dt = k*i  # Change in removed cases, as a %
        di_dt = -(ds_dt + dr_dt)  # Change in infected people, as a %

        # Turning percentages into total numbers
        rnew = int((dr_dt) * N)
        snew = int((ds_dt) * N)
        inew = int((di_dt) * N)

        # Calculating next day's numbers
        R_list.append(R + rnew)
        S_list.append(S + snew)
        I_list.append(I + inew)

        total_list.append(total_list[-1] - snew)  # New cases are equal to -snew
        new_cases_list.append(-snew)
        # New deaths are equal to rnew times the death rate
        deaths_list.append(deaths_list[-1] + int(death_rate[-1] * rnew))
        death_rate.append(death_rate[-1])

        # Printing each days information
        print(str(datetime.date.fromtimestamp(date)) + ": " + str(format(-snew, ',d')) + " new cases and "
              + str(format(total_list[-1], ',d')) + " total cases and "
              + str(format(deaths_list[-1], ',d')) + " deaths.")

    # Updating the data dictionary
    data["Total list"] = total_list
    data["Deaths list"] = deaths_list
    data["R list"] = R_list
    data["I list"] = I_list
    data["S list"] = S_list
    data["New cases list"] = new_cases_list
    data["Date list"] = date_list
    data["Death rate"] = death_rate
    return data


def plotting(data, selection, scale="log"):
    """ This function plots the lists selected from data.
        Arguments:
            -data (dict): The dictionary containing the data from the model.
            -selection (list of str): The list contains the dict keys of the lists that the user wants to plot.
            -scale (keyword, str): Should be either 'log' or 'linear', defines the scale of the y axis."""

    dates = data["Date list"]
    y_axis = []  # The data points to be plotted
    for sel in selection:
        y_axis.append(np.array(data[sel]))
    # Turn Unix timestamps into datetime objects
    for i, date in enumerate(dates):
        dates[i] = datetime.date.fromtimestamp(date)

    t = np.array(dates)
    fig, ax = plt.subplots()
    plt.yscale(scale)
    for pl in y_axis:
        ax.plot(t, pl)

    ax.set(xlabel='Days', ylabel=str(selection),
           title='Flatten the curve, folks')
    ax.grid()

    name = ".\\results\\"
    for sel in selection:
        name += (sel + ", ")
    name = name + str(dates[-1]) + ".png"
    fig.savefig(name)
    plt.show()


if __name__ == '__main__':

    Data = init_data(scenario="without China")
    Data = sir_method(Data, offset=25, run=25)
    plotting(Data, ["Total list", "Deaths list", "I list"], scale='linear')


