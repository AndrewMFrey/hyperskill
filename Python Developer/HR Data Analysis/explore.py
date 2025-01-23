import numpy as np
import pandas as pd
import requests
import os


if __name__ == '__main__':

    if not os.path.exists('../Data'):
        os.mkdir('../Data')

    # Download data if it is unavailable.
    if ('A_office_data.xml' not in os.listdir('../Data') and
            'B_office_data.xml' not in os.listdir('../Data') and
            'hr_data.xml' not in os.listdir('../Data')):
        print('A_office_data loading.')
        url = "https://www.dropbox.com/s/jpeknyzx57c4jb2/A_office_data.xml?dl=1"
        r = requests.get(url, allow_redirects=True)
        open('../Data/A_office_data.xml', 'wb').write(r.content)
        print('Loaded.')

        print('B_office_data loading.')
        url = "https://www.dropbox.com/s/hea0tbhir64u9t5/B_office_data.xml?dl=1"
        r = requests.get(url, allow_redirects=True)
        open('../Data/B_office_data.xml', 'wb').write(r.content)
        print('Loaded.')

        print('hr_data loading.')
        url = "https://www.dropbox.com/s/u6jzqqg1byajy0s/hr_data.xml?dl=1"
        r = requests.get(url, allow_redirects=True)
        open('../Data/hr_data.xml', 'wb').write(r.content)
        print('Loaded.')

        # All data in now loaded to the Data folder.

    # Load dataframes
    A_office_df = pd.read_xml('../Data/A_office_data.xml')
    B_office_df = pd.read_xml('../Data/B_office_data.xml')
    hr_data_df = pd.read_xml('../Data/hr_data.xml')

    # Reindex dataframes
    A_office_df.index = A_office_df['employee_office_id'].map(lambda employee_office_id: f'A{employee_office_id}')
    B_office_df.index = B_office_df['employee_office_id'].map(lambda employee_office_id: f'B{employee_office_id}')
    hr_data_df = hr_data_df.set_index('employee_id')

    # Concat the office dataframes into a single dataframe
    unified_office_df = pd.concat([A_office_df, B_office_df])

    # Merge the unified dataframe with HR data
    merged_df = pd.merge(unified_office_df,
                         hr_data_df,
                         left_index=True,
                         right_index=True,
                         indicator=True)
    # Only keep rows with data from both sets
    merged_df = merged_df[merged_df['_merge'] == 'both']
    # Drop superfluous columns
    merged_df = merged_df.drop(['employee_office_id', '_merge'], axis=1)
    # Sort index (employee_ID)
    merged_df = merged_df.sort_index()

    # Departments of top ten employees in terms of working hours
    print(merged_df.sort_values('average_monthly_hours', ascending=False)['Department'].head(10).to_list())
    # Total projects where IT department employees with low salaries have worked.
    print(merged_df.query("Department == 'IT' & salary == 'low'")['number_project'].sum())
    # Eval scores and satisfaction levels for employees A4, B7064, and A3033
    print(merged_df.loc[['A4', 'B7064', 'A3033'], ['last_evaluation', 'satisfaction_level']].values.tolist())

    # Dataframe for the following:
    # the median number of projects the employees in a group worked on, and how many employees worked on more than five
    # projects;
    # the mean and median time spent in the company;
    # the share of employees who've had work accidents;
    # the mean and standard deviation of the last evaluation score.
    print(merged_df.groupby('left').agg({"number_project": ["median", ("count_bigger_5", lambda x: sum(x > 5))],
                                         "time_spend_company": ["mean", "median"],
                                         "Work_accident": "mean",
                                         "last_evaluation": ["mean", "std"]}).round(2).to_dict())

    # First pivot table:
    # Index = Department
    # Columns = [left, salary]
    # Values = average_monthly_hours
    # Format = median average_monthly_hours
    # Filter = median average_monthly_hours for high-salary < median average_monthly_hours for medium-salary OR
    #          median average_monthly_hours for low-salary < median average_monthly_hours for high-salary
    first_pivot_df = merged_df.pivot_table(index='Department',
                                           columns=["left", "salary"],
                                           values='average_monthly_hours',
                                           aggfunc='median').round(2)
    # Apply required filtering
    first_pivot_df = first_pivot_df.loc[(first_pivot_df[(0, 'high')] < (first_pivot_df[(0, 'medium')])) | (
                first_pivot_df[(1, 'low')] < (first_pivot_df[(1, 'high')]))]
    # Print as a dict
    print(first_pivot_df.to_dict())

    # Second pivot table:
    # Index = time_spend_company
    # Column = promotion_last_5years
    # Values = [satisfaction_level, last_evaluation]
    # Format = max, mean, min last_evaluation
    # Filter = mean last_evaluation for not-promoted > mean last_evaluation for promoted
    second_pivot_df = merged_df.pivot_table(index='time_spend_company',
                                            columns="promotion_last_5years",
                                            values=["satisfaction_level", "last_evaluation"],
                                            aggfunc=["max", "mean", "min"])
    # Apply required filtering
    second_pivot_df = second_pivot_df.loc[second_pivot_df[('mean', 'last_evaluation', 0)] >
                                          second_pivot_df[('mean', 'last_evaluation', 1)]]
    # Print as a dict
    print(second_pivot_df.to_dict())
