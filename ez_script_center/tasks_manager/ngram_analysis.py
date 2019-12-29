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

from io import StringIO

from ez_script_center import celery_worker
from ez_script_center.tasks.scripts import ngram_analysis

from ez_script_center.tasks_manager import register_task


@register_task("n_gram_analysis")
@celery_worker.task(bind=True)
def execute_ngram_analysis(
    self,
    data,
    lemmatize=False,
):
    """The main function that takes in the path to the .csv with raw
    data and returns the dict containing performance for each ngram.

    Saves the analysis to .xlsx file.

    Args:
        - input_file (str): The relative path to the raw data file in a
            csv format.
        - output_folder (str, optional): The relative path to which the
            output .xlsx files should be written.
            Defaults to "ngram_analysis"
        - output_file_prefix (str, optional): The prefix that will be
            attached to the .xlsx file containing the analysis.
        - lemmatize (bool, optional): If set to True the cleaned data
            will also be very conservatively lemmatized, trying to
            normalize only words that are more or less sure with
            omitting word that have special characters in them.
            Defaults to False.

    Returns:
        - dict: A dictionary containing key value pairs of the ngram
            and ngram's performance DataFrame.

            {
                "1-gram": DataFrame({
                    "1-gram": ["jack", "and", "jill"],
                    "link_clicks": [1000, 3000, 2000],
                    "in_ads": ["ad_1", "ad_1, ad_2", "ad_2"]
                }),
                "2-gram": DataFrame({
                    "2-gram": ["jack and", "and jill"],
                    "link_clicks": [1000, 2000],
                    "in_ads": ["ad_1", "ad_2"]
                })
            }

    Notes:
        - Also saves the output to an .xlsx formatted file.
        - Requirements for the input .csv file:
            * The first column is required to be the text that you
                wish to be analyzed, rest of the columns is
                performance data.
            * The performance data shouldn't be calculated in any
                way (averages, ROI, etc.) as thiswill simply
                return nonsense data due to summing them up.
    """
    self.update_state(
        state="PROGRESS",
        meta={'current': 0, 'total': 5, 'status': "Starting..."}
    )

    if lemmatize:
        spacy.load("en-core-web-sm")

    self.update_state(
        state="PROGRESS",
        meta={'current': 1, 'total': 5, 'status': f"Reading {input_file}"}
    )

    input_data_df = pd.read_csv(StringIO(input_file))

    self.update_state(
        state="PROGRESS",
        meta={'current': 2, 'total': 5,
              'status': f"Cleaning and processing input data..."}
    )

    input_data_cleaned_df = ngram_analysis.clean_input_data(input_data_df, lemmatize=lemmatize)
    input_data_with_ngrams_df = ngram_analysis.create_ngrams(input_data_cleaned_df)

    self.update_state(
        state="PROGRESS",
        meta={'current': 3, 'total': 5,
              'status': f"File cleaning and processing done..."}
    )

    self.update_state(
        state="PROGRESS",
        meta={'current': 4, 'total': 5,
              'status': f"Calculating performance..."}
    )

    ngram_performance_dict = calculate_ngram_performance(input_data_with_ngrams_df)
    # Need to change the inner dataframes to csv strings.

    return {'state': 'SUCCESS',
            'current': 5, 'total': 5,
            'status': "Performance calculated.",
            'result': ngram_performance_dict}

