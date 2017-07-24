import copy


def highest_metric_value(df, metric, param):
    """Pick the model group with the highest metric value

    Arguments:
        metric (string) -- model evaluation metric, such as 'precision@'
        metric_param (string) -- model evaluation metric parameter,
            such as '300_abs'
        df (pandas.DataFrame) -- dataframe that is keyed on model group id,
            containing the columns:
                model_id,
                train_end_time,
                metric,
                parameter,
                raw_value,
                below_best,
                below_best_next_time
    Returns: (int) the model group id to select, with highest raw metric value
    """
    return df[df['raw_value'] == df['raw_value'].max()].index.tolist()[0]


SELECTION_RULES = {
    'highest_metric_value': highest_metric_value,
}


class RegretCalculator(object):
    def __init__(self, distance_from_best_table):
        self.distance_from_best_table = distance_from_best_table

    def regrets_for_rule(
        self,
        selection_rule,
        model_group_ids,
        train_end_times,
        metric,
        metric_param,
        selection_rule_args
    ):
        """Calculate the regrets, or distance between the chosen model and
            the maximum value next test time

        Arguments:
            selection_rule
            model_group_ids
            train_end_times
            metric
            metric_param

        Returns: (list) for each train end time, the distance between the
            model group chosen by the selection rule and the potential
            maximum for the next train end time
        """
        regrets = []
        df = self.distance_from_best_table.as_dataframe(model_group_ids)

        for train_end_time in train_end_times:
            localized_df = copy.deepcopy(
                df[df['train_end_time'] <= train_end_time]
            )
            del localized_df['below_best_next_time']

            choice = selection_rule(localized_df, **selection_rule_args)
            regret_result = df[
                (df['model_group_id'] == choice)
                & (df['train_end_time'] == train_end_time)
                & (df['metric'] == metric)
                & (df['parameter'] == metric_param)
            ]
            assert len(regret_result) == 1
            regrets.append(regret_result['below_best_next_time'].values[0])
        return regrets