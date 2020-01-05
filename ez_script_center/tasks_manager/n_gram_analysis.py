"""
Script for performing a range n-gram split on passed data.

TODO:
* Support multi-processing < for the n-gram performance calculations
    wait for swifter module update.
    For now making it multi-processing friendly may actually slow it
    down due to calling overheads. Pandas' apply is sufficient.
* Support automatic downloading of data from Facebook and Google Ads.

* Known issues - https://github.com/explosion/spaCy/issues/3665
"""

from io import StringIO, BytesIO, TextIOWrapper

from ez_script_center.tasks_manager import TasksManager, TaskBase
from ez_script_center import s3

from ez_script_center import celery_worker
from ez_script_center.tasks_manager.scripts import ngram_analysis


@TasksManager.register_task()
@celery_worker.task(bind=True, base=TaskBase)
def execute_ngram_analysis(
    self,
    data,
    lemmatize=False,
):
    """The main function that takes in the path to the .csv with raw
    data and returns the dict containing performance for each ngram.

    Saves the analysis to .xlsx file.

    Args:
        - data (dict): The data dictionary containing a files key and
            input_args key.
            "input_files" key: contains a dict with form field name as
            key and s3 file key as value.
            "input_info": contains another dict-like object with form
            field names as key and values corresponding to what the user
            has passed in.
        - lemmatize (bool, optional): If set to True the cleaned data
            will also be very conservatively lemmatized, trying to
            normalize only words that are more or less sure with
            omitting word that have special characters in them.
            Defaults to False.

    Returns:
        - dict: A dictionary with two keys - result_files and
            result_info.
            "result_files" key: contains a dict with form field name as
            key and s3 file key as value.
            "result_info" key: contains another dict object.
    """
    self.update_state(
        state="PROGRESS",
        meta={'current': 0, 'total': 5, 'progressbar_message': "Starting..."}
    )

    if lemmatize:
        ngram_analysis.spacy.load("en-core-web-sm")

    # Convert the downloaded BytesIO object to a StringIO one so
    # pd.read_csv can use it.
    filename, input_file = s3.download_fileobj(data["input_files"]["copy_performance"])
    input_file = TextIOWrapper(input_file, encoding='utf-8')
    input_file.seek(0)

    self.update_state(
        state="PROGRESS",
        meta={'current': 1, 'total': 5, 'progressbar_message': f"Reading {filename}"}
    )

    input_data_df = ngram_analysis.pd.read_csv(input_file)

    self.update_state(
        state="PROGRESS",
        meta={'current': 2, 'total': 5,
              'progressbar_message': f"Cleaning and processing input data..."}
    )

    input_data_cleaned_df = ngram_analysis.clean_input_data(input_data_df, lemmatize=lemmatize)
    input_data_with_ngrams_df = ngram_analysis.create_ngrams(input_data_cleaned_df)

    self.update_state(
        state="PROGRESS",
        meta={'current': 3, 'total': 5,
              'progressbar_message': f"File cleaning and processing done..."}
    )

    self.update_state(
        state="PROGRESS",
        meta={'current': 4, 'total': 5,
              'progressbar_message': f"Calculating performance..."}
    )

    ngram_performance_dict = ngram_analysis.calculate_ngram_performance(input_data_with_ngrams_df)

    # Drop the file into a BytesIO file-like object so it can be safely
    # uploaded to s3
    return_file = BytesIO()
    writer = ngram_analysis.pd.ExcelWriter(return_file, engine="xlsxwriter")
    for ngram, performance_df in ngram_performance_dict.items():
        performance_df.to_excel(writer, sheet_name=ngram, index=False)
    writer.close()
    return_file.seek(0)

    return_file = {f"Analysis of {filename.split('.')[0]}.xlsx": return_file}

    return self.create_result_payload(
        progressbar_message="Performance calculated.",
        files=return_file
    )
