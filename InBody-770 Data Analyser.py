import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
from datetime import datetime as dt
import os
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog

def main():
    print("Welcome to the InBody-770 Data Analyser.", end='\n\n')
    input("Press Enter to choose the working directory.")
    root = tk.Tk()
    root.withdraw()
    directory = filedialog.askdirectory()
    print("Working Directory: " + directory, end='\n\n')
    while True:
        print("Options: ")
        print("1. New Data from InBody")
        print("2. Merge Data Sheets")
        print("3. Create User Sheets")
        print("4. Generate Plots")
        print("5. Exit")
        choice_1 = user_input('int', "Enter your choice: ", "Invalid input. Try Again.", range=[1,2,3,4,5])
        if choice_1 in [1, 3, 4]: 
            main_data = clean_data(extract_data(directory=directory), choice_1)
            if choice_1 == 1:
                create_new_file(main_data, 'Processed Data ' + str(dt.now()) + '.xlsx', directory)
            else:
                user_dict = create_user_dfs(main_data)
                if choice_1 == 3:
                    create_new_file(user_dict, 'New User Sheets ' + str(dt.now()) + '.xlsx', directory)
                else:
                    print('Plotting Options: ')
                    choice_2 = user_input('int', "A. Users' Data, 1) Single or 2) All: ", "Invalid input. Try Again.", range=[1,2])
                    if choice_2 == 1:
                        user = '<' + input("Enter ID: ") + '>'
                        while user not in user_dict.keys():
                            print("Invalid ID.")
                            user = '<' + input("Enter ID: ") + '>'
                    else:
                        user = None
                    time_increment = user_input('int', "B. Time Increment, 1) Day, 2) Week, 3) 2-Weeks, or 4) Month: ", "Invalid input. Try Again.", range=[1,2,3,4,5], reference={1: 'Day',2: 'Week', 3: 'Biweekly Number', 4: 'Month'})
                    choice_3 = user_input('int', "C. Metrics, 1) Single or 2) All: ", "Invalid input. Try Again.", range=[1,2])
                    if choice_3 == 1:
                        print("List of metrics that can be plotted: ")
                        # creating a temporary dictionary for listed index and column name
                        temp_dict = {}
                        display_counter = 1
                        for column in list(main_data.columns):
                            if column not in ['ID', 'Year', 'Week', 'Month', 'Date', 'Gender', 'Height', 'Age', 'Day', 'Biweekly Number']:
                                temp_dict[display_counter] = column
                                print(str(display_counter) + ". " + column)
                                display_counter += 1
                        metric = temp_dict[user_input('int', "Choose the metric to plot: ", "Invalid input. Try Again.", range=temp_dict.keys())]
                    else:
                        metric = None
                    
                    filtered_dict = filter_data(user_dict, metric, user)  # filter the data
                    filtered_dict = process_data(filtered_dict, time_increment)  # process the data to be along the selected time increment
                    filtered_dict = collate_data(filtered_dict, time_increment)  # collate the data and interpolate if required
                    
                    # making a folder to store the plots
                    folder = os.path.join(directory,('Plots ' + str(dt.now())).replace(':', '-'))
                    os.mkdir(folder)

                    endpoints = user_input("str", "Would you like to plot only the start and end points? (Y/N): ", "Invalid input. Try Again.", range=['Y', 'y', 'N', 'n'], reference={'Y':True, 'y':True, 'N':False, 'n':False})

                    if choice_2 == 1:
                        if endpoints:
                            filtered_dict[user] = filtered_dict[user].iloc[[0, -1]]
                        create_new_file(filtered_dict[user], 'Plotted Data ' + str(dt.now()) + '.xlsx', directory)
                        if choice_3 == 1:
                            plot_data(folder, filtered_dict[user].index.tolist(), filtered_dict[user][metric], time_increment, metric)
                        elif choice_3 == 2:
                            for metric in filtered_dict[list(filtered_dict.keys())[0]].columns:
                                if metric not in ['Date', 'Year', 'Week', 'Day', 'Biweekly Number', 'Month', 'ID', 'Gender', 'Height', 'Age']:
                                    plot_data(folder, filtered_dict[user].index.tolist(), filtered_dict[user][metric], time_increment, metric)
                    elif choice_2 == 2:
                        choice_4 = user_input('int', "D. 1) Lines for Each User or 2) An Aggregate Line: ", "Invalid input. Try Again.", range=[1,2])
                        if choice_4 == 1:
                            if endpoints:
                                for user in filtered_dict.keys():
                                    filtered_dict[user] = filtered_dict[user].iloc[[0, -1]]
                            create_new_file(filtered_dict, 'Plotted Data ' + str(dt.now()) + '.xlsx', directory)
                            if choice_3 == 1:
                                time_series = [filtered_dict[user].index.tolist() for user in filtered_dict.keys()]
                                data_series = [filtered_dict[user][metric].tolist() for user in filtered_dict.keys()]
                                plot_data(folder, time_series, data_series, time_increment, metric, multiple=1)
                            elif choice_3 == 2:
                                for metric in filtered_dict[list(filtered_dict.keys())[0]].columns:
                                    time_series = [filtered_dict[user].index.tolist() for user in filtered_dict.keys()]
                                    data_series = [filtered_dict[user][metric].tolist() for user in filtered_dict.keys()]
                                    if metric not in ['Date', 'Year', 'Week', 'Day', 'Biweekly Number', 'Month', 'ID', 'Gender', 'Height', 'Age']:
                                        plot_data(folder, time_series, data_series, time_increment, metric, multiple=1)
                        elif choice_4 == 2:
                            aggregate_df = aggregate_data(filtered_dict)
                            if endpoints:
                                aggregate_df = aggregate_df.iloc[[0, -1]]
                            create_new_file(aggregate_df, 'Plotted Data ' + str(dt.now()) + '.xlsx', directory)
                            if choice_3 == 1:
                                plot_data(folder, aggregate_df.index.tolist(), aggregate_df[metric], time_increment, metric + " (Aggregate of " + str(len(filtered_dict.keys())) + " Users)")
                            elif choice_3 == 2:
                                for metric in aggregate_df.columns:
                                    if metric not in ['Date', 'Year', 'Week', 'Day', 'Biweekly Number', 'Month', 'ID', 'Gender', 'Height', 'Age']:
                                        plot_data(folder, aggregate_df.index.tolist(), aggregate_df[metric], time_increment, metric + " (Aggregate of " + str(len(filtered_dict.keys())) + " Users)")
                    print("Plots generated and saved.")
        elif choice_1 == 2:
            print("Merging Options: ")
            print("1. Raw InBody Data")
            print("2. User Data Sheets")
            choice_2 = user_input('int', "Enter your choice: ", "Invalid input. Try Again.", range=[1,2])
            num_files = user_input('int', "Enter the number of files to merge: ", "Invalid input. Try Again.")
            files = [extract_data(prompt="Enter file name " + str(i + 1) + ": ", directory=directory) for i in range(num_files)]
            if choice_2 == 1:
                main_data = pd.DataFrame(columns=list(files[0].columns))
                for file in files:
                    main_data = pd.concat([main_data, file])
                main_data = clean_data(main_data, choice_1)
                create_new_file(main_data, 'Merged Data ' + str(dt.now()) + '.xlsx', directory=directory)
            else:
                user_dict = {}
                for file in files:
                    for iden in file.keys():
                        if iden not in user_dict.keys():
                            user_dict[iden] = file[iden]
                        user_dict[iden] = pd.concat([user_dict[iden], file[iden]])
                for user in user_dict.keys():
                    user_dict[user] = clean_data(user_dict[user], choice_1)
                new_user_sheets_name = 'Merged User Sheets ' + str(dt.now()) + '.xlsx'
                with pd.ExcelWriter(new_user_sheets_name) as writer:
                    for user, df in user_dict.items():
                        df.to_excel(writer, sheet_name=str(user), index=False)
                print("Merged User Sheets File created, called " + new_user_sheets_name + ".")
            print("Files merged.")
        else:
            print("Goodbye.")
            break
        print()

def extract_data(sheets=False, filepath=None, sheet_name=None, prompt=None, sheet_prompt=False, response=False, directory=os.getcwd()):
    while True:
        try:
            if prompt == None:
                prompt = "Enter file name: "
            if sheets and sheet_prompt == None:
                sheet_prompt = "Enter sheet name: "
            if filepath != None:
                if filepath[-5:] != '.xlsx':
                    filepath += '.xlsx'
            else:
                filepath = directory + '/' + input(prompt) + '.xlsx'
            data = pd.read_excel(filepath, sheet_name=input(sheet_prompt) if (sheet_name == None) else sheet_name) if sheets else pd.read_excel(filepath)
            print()
            return data
        except:
            if not response:
                print("File or Sheet not found. Try Again.", end='\n\n')
                filepath = None
            else:
                print(response)
            continue
            
def delete_column_with_term(df, term):
    # Removes the columns with the term in the title from dataframe
    for col in df.columns:
        if term in col:
            df = df.drop(columns=[col])
    print("Columns with '" + term + "' removed.")
    return df

def create_user_dfs(df):
    # Creates a dictionary of dataframes, with each dataframe containing the data for one user
    unique_ids = df['ID'].unique()
    user_dict = {}
    for id in unique_ids:
        user_dict[id] = df.loc[df["ID"] == id].reset_index(drop=True)
    return user_dict

def create_new_file(df, name, directory=os.getcwd()):
    name = name.replace(':', '-')
    if type(df) == dict:
        with pd.ExcelWriter(os.path.join(directory, name)) as writer:
            for user, df in df.items():
                df.to_excel(writer, sheet_name=str(user), index=False)
    else:
        with pd.ExcelWriter(os.path.join(directory, name)) as writer:
            df.to_excel(writer, index=False)
    print("New Data File created, called " + name + ".")

def clean_data(df, choice):
    # remove the columns that are not needed
    for column in ['Limit', 'Impedence','Phase Angle', 'Reactance']:
        df = delete_column_with_term(df, column)
    df = df.drop(list(set(list(df.columns)).intersection(['207. Growth Score', '208. Obesity Degree of a Child', '211. Systolic', '212. Diastolic', 
                '213. Pulse', '214. Mean Artery Pressure', '215. Pulse Pressure', '216. Rate Pressure Product', '217. SMI', '218. Recommended Calorie Intake', 
                '221. Systolic2', '222. Diastolic2', '223. Pulse2', '224. Mean Artery Pressure2', '225. Pulse Pressure2', '226. Rate Pressure Product2', 
                '123. InBody Score'])), axis=1)
    # remove the numbers from the start of the column names
    for j in range(len(df.columns)):
        for i in range(len(df.columns[j])):
            if df.columns[j][i] == '.':
                df.rename(columns={df.columns[j]: df.columns[j][i+2:]}, inplace=True)
                break
    df = df = df.drop_duplicates(subset=['Test Date / Time'], keep='first')
    print("Duplicates removed.", end='\n\n')

    if choice == 4:
        # Further cleaning and organising the data for before plotting
        # Separating the Test Date / Time column into two columns for date and time
        df.insert(4, 'Date', '')
        df.insert(5, 'Time', '')
        df[['Date', 'Time']] = df['Test Date / Time'].str.split(' ', expand=True)
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        df = df.drop(columns=['Test Date / Time'])
        df = df.drop(columns=['Time'])

        # Changing data in particular columns to numbers for easier processing
        df['Gender'] = df['Gender'].apply(lambda x: 0 if x == 'M' else 1)
        df['VFL (Visceral Fat Level)'] = df['VFL (Visceral Fat Level)'].apply(lambda x: int(x[6:]))

        # creating new columns for the year, day, week, biweekly number, and month
        df.insert(5, 'Year', 0)
        df.insert(6, 'Day', 0)  # day of the year
        df.insert(7, 'Week', 0)
        df.insert(8, 'Biweekly Number', 0)
        df.insert(9, 'Month', 0)
        df['Year'] = df['Date'].apply(lambda x: pd.to_datetime(x, dayfirst=True).isocalendar()[0])
        df['Day'] = df['Date'].apply(lambda x: pd.to_datetime(x, dayfirst=True).dayofyear)
        df['Week'] = df['Date'].apply(lambda x: pd.to_datetime(x, dayfirst=True).isocalendar()[1])
        df['Biweekly Number'] = df['Week'].apply(lambda x: int((x - 1) / 2) + 1)
        df['Month'] = df['Date'].apply(lambda x: pd.to_datetime(x, dayfirst=True).month)

        df = df.sort_values(by=['ID', 'Date']).reset_index(drop=True)

    return df

def filter_data(data_dict, selected_metric, selected_user):
    # filter the data based on various parameters
    if selected_user != None:
        data_dict = {selected_user: data_dict[selected_user]}
    while True:
        choice = user_input('str', "Would you like to filter by any other metrics? (Y/N): ", "Invalid input. Try Again.", range=['Y', 'y', 'N', 'n'])
        if choice == 'Y' or choice == 'y':
            startpoint = user_input('int', "Would you like to filter by 1) Startpoint or 2) All Data: ", "Invalid input. Try Again.", range=[1,2], reference={1:True, 2:False}) if selected_user == None else False
            if startpoint:
                startpoint_df = pd.DataFrame(columns=list(data_dict[list(data_dict.keys())[0]].columns))
                for user in data_dict.keys():
                        startpoint_df.loc[len(startpoint_df)] = data_dict[user].iloc[0]
            print("List of metrics that can be filtered: ")
            # creating a temporary dictionary for listed index and column name
            list_dict = {}
            display_counter = 1
            discounted_columns = ['ID', 'Year', 'Week', 'Day', 'Biweekly Number', 'Month'] if selected_user == None else ['ID', 'Year', 'Week', 'Day', 'Biweekly Number', 'Month', 'Height', 'Gender', 'Age']
            for column in list(data_dict[list(data_dict.keys())[0]].columns):
                if column not in discounted_columns:
                    list_dict[display_counter] = column
                    print(str(display_counter) + ". " + column)
                    display_counter += 1
            # asking the user to choose a metric to filter by
            metric = list_dict[user_input('int', "Enter the number of the metric you would like to filter by: ", "Invalid input. Try Again.", range=list_dict.keys())]
            val_or_range = user_input('int', "Would you like to filter by 1) Value or 2) Range: ", "Invalid input. Try Again.", range=[1,2])
            while True:
                try:
                    filtered_dict = data_dict.copy()
                    if val_or_range == 1:
                        value = user_input('int', "Enter value: ", "Invalid input. Try Again.") if metric != 'Date' else pd.to_datetime(user_input('date', "Enter date (dd/mm/yyyy): ", "Invalid input. Try Again.")).date()
                        if startpoint:
                                startpoint_df = startpoint_df.loc[startpoint_df[metric] == value]
                        else:
                            for user in filtered_dict.keys():
                                filtered_dict[user] = filtered_dict[user].loc[filtered_dict[user][metric] == value]
                    elif val_or_range == 2:
                        min = user_input('int', "Enter minimum value: ", "Invalid input. Try Again.") if metric != 'Date' else pd.to_datetime(user_input('date', "Enter earliest date (dd/mm/yyyy): ", "Invalid input. Try Again.")).date()
                        max = user_input('int', "Enter maximum value: ", "Invalid input. Try Again.") if metric != 'Date' else pd.to_datetime(user_input('date', "Enter latest date (dd/mm/yyyy): ", "Invalid input. Try Again.")).date()
                        if startpoint:
                            startpoint_df = startpoint_df.loc[(startpoint_df[metric] >= min) & (startpoint_df[metric] <= max)]
                        else:
                            for user in filtered_dict.keys():
                                filtered_dict[user] = filtered_dict[user].loc[(filtered_dict[user][metric] >= min) & (filtered_dict[user][metric] <= max)]
                    if startpoint:
                        users = startpoint_df['ID'].tolist()
                        for user in list(filtered_dict.keys()):
                            if user not in users:
                                del filtered_dict[user]
                    
                    # check if all the dataframes are empty
                    all_empty = True
                    for df in filtered_dict.values():
                        if not df.empty:
                            all_empty = False
                            break

                    if all_empty:
                        print("No data found meeting filter condition.")
                        print("Filter not applied.")
                        continue
                    else:
                        # replace the original data dictionary with the filtered data dictionary
                        data_dict = filtered_dict
                        print("Data filtered.")
                    break
                except:
                    print("Invalid input.")
                    continue
        else:
            break

    if selected_metric != None:
        # cycle through each user in the dictionary and delete the columns that are not the metric, 'ID', 'Date', 'Year', 'Day', 'Week', 'Biweekly Number', or 'Month'
        for user in data_dict.keys():
            for column in list(data_dict[user].columns):
                if column not in [selected_metric, 'ID', 'Date', 'Year', 'Week', 'Month', 'Biweekly Number','Day']:
                    data_dict[user] = data_dict[user].drop(columns=[column])

    # reset the index of each dataframe
    for user in data_dict.keys():
        data_dict[user] = data_dict[user].reset_index(drop=True)

    return data_dict

def process_data(data_dict, time_increment):
    # delete the ID, Date, and unused time increment columns from each dataframe
    for user in data_dict.keys():
        data_dict[user] = data_dict[user].drop(columns=['ID'])
        data_dict[user] = data_dict[user].drop(columns=['Date'])
        # drop multiple columns from a dataframe
        for col in ['Week', 'Day', 'Month', 'Biweekly Number']:
            if time_increment != col:
                data_dict[user] = data_dict[user].drop(columns=col)
    
    # loop through each dataframe, combine data for separate dates into selected time increments
    for user in data_dict.keys():
        data_dict[user] = data_dict[user].sort_values(by=['Year', time_increment]).reset_index(drop=True)
        time_increment_avg_df = pd.DataFrame(columns=list(data_dict[user].columns))
        years = data_dict[user]['Year'].unique()
        for year in years:
            time_increment_list = data_dict[user].loc[data_dict[user]['Year'] == year][time_increment].unique()
            for increment in time_increment_list:
                # set time_increment_avg_df to the mean of the data for the currently indexed year and increment
                time_increment_avg_df.loc[len(time_increment_avg_df)] = data_dict[user].loc[(data_dict[user]['Year'] == year) & (data_dict[user][time_increment] == increment)].mean(axis=0)
        # replacing the original dataframe with the processed data
        data_dict[user] = time_increment_avg_df

    # scan the dataframes dcitionary to find the time increments that are missing data, and add rows of NaN values to the dataframe for those increments
    for user in list(data_dict.keys()):
        years = data_dict[user]['Year'].unique()
        for year in years:
            time_increment_list = data_dict[user].loc[data_dict[user]['Year'] == year][time_increment].unique()
            time_increment_list = [int(i) for i in time_increment_list]
            min_inc, max_inc = min(time_increment_list), max(time_increment_list)
            for increment in range(min_inc, max_inc + 1):
                if increment not in time_increment_list:
                    data_dict[user].loc[len(data_dict[user])] = [None] * (len(data_dict[user].columns))
                    data_dict[user].loc[len(data_dict[user]) - 1, 'Year'] = year
                    data_dict[user].loc[len(data_dict[user]) - 1, time_increment] = increment
        # sort the dataframe by year and time increment
        data_dict[user] = data_dict[user].sort_values(by=['Year', time_increment]).reset_index(drop=True)
        data_dict[user] = data_dict[user].reset_index(drop=True)

    period = user_input('int', "Minimum time period for plot to cover (units in selected increments, 0 to cover entire period): ", "Invalid input. Try Again.")
    if period != 0:
        for user in list(data_dict.keys()):
            if len(data_dict[user]) < period:
                del data_dict[user]
        print("Users without data spanning the time period deleted.")
    else:    
        print("All user data included.")

    return data_dict

def collate_data(data_dict, time_increment):
    # collate the data, accounting for time points with missing data and interpolating if required
    while True:
        print("Checking for missing data...")
        # dictionary to store the indices for which users are missing data
        missing_index_dict = {}
        for user in data_dict.keys():
            years = data_dict[user]['Year'].unique()
            for year in years:
                time_increment_list = data_dict[user].loc[data_dict[user]['Year'] == year][time_increment].unique()
                for increment in time_increment_list:
                    row = data_dict[user].loc[(data_dict[user]['Year'] == year) & (data_dict[user][time_increment] == increment)].drop(['Year', time_increment], axis=1)
                    if row.isna().values.any():
                        if row.index[0] not in missing_index_dict.keys():
                            missing_index_dict[row.index[0]] = [[], 0]
                        missing_index_dict[row.index[0]][0].append(user)
        
        if len(missing_index_dict.keys()) == 0:
            print("No missing data.")
            return data_dict
        
        # append the percentage of users missing data at each time point to the missing_index_dict
        for index in missing_index_dict.keys():
            missing_index_dict[index][1] = round(len(missing_index_dict[index][0]) / len(data_dict.keys()) * 100, 2)

        # sort the missing_index_dict by the percentage of users missing data at each time point
        missing_index_dict = dict(sorted(missing_index_dict.items(), key=lambda item: item[1][1], reverse=True))

        # dictionary to store the number of time points with missing data for each user
        missing_data_dict = {}
        for users in missing_index_dict.values():
            for user in users[0]:
                if user not in missing_data_dict.keys():
                    missing_data_dict[user] = [0, 0]
                missing_data_dict[user][0] += 1
        
        # append the percentage of missing data for each user to the missing_data_dict
        for user in missing_data_dict.keys():
            missing_data_dict[user][1] = round((missing_data_dict[user][0] / len(data_dict[user])) * 100, 2)

        # sort the missing_data_dict by the percentage of missing data for each user
        missing_data_dict = dict(sorted(missing_data_dict.items(), key=lambda item: item[1][1], reverse=True))

        missing_data = 0
        for user in missing_data_dict.keys():
            missing_data += missing_data_dict[user][0]

        total_data = 0
        for user in data_dict.keys():
            total_data += len(data_dict[user])
            
        print("----------Missing Data Summary----------")
        print("Percentage of Data Missing: " + str(round((missing_data / total_data) * 100, 2)) + "%", end='\n\n')
        print("Users and percentage of data they are missing: ")
        # print the users and the percentage of data they are missing in 3 columns
        for i in range(0, len(list(missing_data_dict.keys())), 3):
            print(list(missing_data_dict.keys())[i] + ": " + str(missing_data_dict[list(missing_data_dict.keys())[i]][1]) + "%", end='\t\t')
            if i + 1 < len(list(missing_data_dict.keys())):
                print(list(missing_data_dict.keys())[i + 1] + ": " + str(missing_data_dict[list(missing_data_dict.keys())[i + 1]][1]) + "%", end='\t\t')
            if i + 2 < len(list(missing_data_dict.keys())):
                print(list(missing_data_dict.keys())[i + 2] + ": " + str(missing_data_dict[list(missing_data_dict.keys())[i + 2]][1]) + "%")
        print("\n")
        print("Time Points and percentage of users missing data at that time point: ")
        # print the time points and the percentage of users missing data at that time point in 3 columns
        for i in range(0, len(list(missing_index_dict.keys())), 3):
            print(str(list(missing_index_dict.keys())[i]) + ": " + str(missing_index_dict[list(missing_index_dict.keys())[i]][1]) + "%", end='\t\t')
            if i + 1 < len(list(missing_index_dict.keys())):
                print(str(list(missing_index_dict.keys())[i + 1]) + ": " + str(missing_index_dict[list(missing_index_dict.keys())[i + 1]][1]) + "%", end='\t\t')
            if i + 2 < len(list(missing_index_dict.keys())):
                print(str(list(missing_index_dict.keys())[i + 2]) + ": " + str(missing_index_dict[list(missing_index_dict.keys())[i + 2]][1]) + "%")
        print("\n")
        print("Collation Options: ")
        print("1. Interpolate Missing Data")
        print("2. Delete the Time Points with Missing Data")
        print("3. Delete the Users with Missing Data")
        choice = user_input('int', "Enter your choice: ", "Invalid input. Try Again.", range=[1,2,3])
        if choice == 1:
            data_dict[user] = data_dict[user].interpolate(method='linear', limit_direction='both')
            print("Missing data interpolated.", end='\n\n')
            return data_dict
        elif choice == 2:
            print("Time Point deletion options: ")
            print("1. Delete all Time Points with missing data for any User")
            print("2. Delete specific Time Points with missing data")
            print("3. Delete Time Points with missing data for a percentage of Users")
            choice_1 = user_input('int', "Enter your choice: ", "Invalid input. Try Again.", range=[1,2,3])
            if choice_1 == 1:
                for index in list(missing_index_dict.keys()):
                    for user in list(data_dict.keys()):
                        data_dict[user] = data_dict[user].drop(index=index)
                    del missing_index_dict[index]
            elif choice_1 == 2:
                while True:
                    index = user_input('int', "Enter the index of the time point to delete: ", "Invalid input. Try Again.")
                    if index in list(missing_index_dict.keys()):
                        for user in list(data_dict.keys()):
                            data_dict[user] = data_dict[user].drop(index=index)
                        del missing_index_dict[index]
                        if input("Delete another time point? (Y/N): ").capitalize == 'Y':
                            continue
                        break
                    else:
                        print("No users missing data at that time point.")
                        continue
            elif choice_1 == 3:
                elimination_factor = user_input('float', "Enter percentage to qualify for elimination: ", "Invalid input. Try Again.")
                for index in list(missing_index_dict.keys()):
                    if missing_index_dict[index][1] >= elimination_factor:
                        for user in list(data_dict.keys()):
                            data_dict[user] = data_dict[user].drop(index=index)
                        del missing_index_dict[index]
            print("Time points deleted according to selection.")
        elif choice == 3:
            print("User deletion options: ")
            print("1. Delete all the Users with any missing data points")
            print("2. Delete specific Users with Missing Data")
            print("3. Delete Users with a certain percentage of missing data")
            choice_1 = user_input('int', "Enter your choice: ", "Invalid input. Try Again.", range=[1,2,3])
            if choice_1 == 1:
                for user in list(missing_data_dict.keys()):
                    del data_dict[user]
                    del missing_data_dict[user]
            elif choice_1 == 2:
                while True:
                    user = '<' + input("Enter ID: ") + '>'
                    if user in list(missing_data_dict.keys()):
                        del data_dict[user]
                        del missing_data_dict[user]
                        if input("Delete another user? (Y/N): ").capitalize == 'Y':
                            continue
                        break
                    else:
                        print("No missing data for that user.")
                        continue
            elif choice_1 == 3:
                elimination_factor = user_input('float', "Enter percentage to qualify for elimination: ", "Invalid input. Try Again.")
                for user in list(missing_data_dict.keys()):
                    if missing_data_dict[user][1] >= elimination_factor:
                        del data_dict[user]
                        del missing_data_dict[user]
            print("Users deleted according to selection.")
        print()

def aggregate_data(data_dict):
    # aggregate the data for all users to plot an average line
    avg_df = pd.DataFrame(columns=list(data_dict[list(data_dict.keys())[0]].columns))
    # find the number of data points to plot
    points_cap = min([len(data_dict[user]) for user in data_dict.keys()])
    for i in range(points_cap):
        temp_df = pd.DataFrame(columns=list(data_dict[list(data_dict.keys())[0]].columns))
        for user in data_dict.keys():
            temp_df = pd.concat([temp_df, data_dict[user].loc[data_dict[user].index == i]], ignore_index=True)
        avg_df.loc[len(avg_df)] = temp_df.mean(axis=0)
    return avg_df.reset_index(drop=True)

def plot_data(folder, x, y, x_label, y_label, multiple=0):
    plt.figure(figsize=(8,6))
    if multiple == 0:
        plt.plot(x, y)
    else:
        for i in range(len(x)):
            plt.plot(x[i], y[i])
    plt.title(y_label + ' vs ' + x_label)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.savefig(folder + '/' + (y_label + ' vs ' + x_label).replace('/','-') + '.png')
    plt.close()

def user_input(type, message, error_message, range=None, reference=None):
    while True:
        try:
            if type == 'int':
                user_input = int(input(message))
            elif type == 'float':
                user_input = float(input(message))
            elif type == 'str':
                user_input = input(message)
            elif type == 'date':
                user_input = dt.strptime(input(message), r'%d/%m/%Y')
            elif type == 'time':
                user_input = dt.strptime(input(message), '%H:%M:%S')
            if range != None:
                if user_input in range:
                    print()
                    if reference != None:
                        return reference[user_input]
                    return user_input
                else:
                    print(error_message)
                    print()
                    continue
            else:
                print()
                return user_input
        except:
            print(error_message)
            print()
            continue

main()