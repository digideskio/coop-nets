import numpy as np
# Bootstrap CI's are not very robust; disabled for now
# import bootstrap

from bt import config


def evaluate(learner, eval_data, metrics, metric_names=None, split_id=None):
    '''
    Evaluate `learner` on the instances in `eval_data` according to each
    metric in `metric`, and return a dictionary summarizing the values of
    the metrics.

    Dump the predictions, scores, and metric summaries in JSON format
    to "{predictions|scores|results}.`split_id`.json" in the run directory.

    :param learner: The model to be evaluated.
    :type learner: bt.learner.Learner

    :param eval_data: The data to use to evaluate the model.
    :type eval_data: list(bt.instance.Instance)

    :param metrics: An iterable of functions that defines the standard by
        which predictions are evaluated.
    :type metrics: Iterable(function(eval_data: list(bt.instance.Instance),
                                     predictions: list(output_type),
                                     scores: list(float)) -> list(float))
    '''
    if metric_names is None:
        metric_names = [
            (metric.__name__ if hasattr(metric, '__name__')
             else ('m%d' % i))
            for i, metric in enumerate(metrics)
        ]

    split_prefix = split_id + '.' if split_id else ''
    results = {}

    predictions, scores = learner.predict_and_score(eval_data)
    config.dump(predictions, 'predictions.%sjsons' % split_prefix, lines=True)
    config.dump(scores, 'scores.%sjsons' % split_prefix, lines=True)

    for metric, metric_name in zip(metrics, metric_names):
        prefix = split_prefix + (metric_name + '.' if metric_name else '')

        inst_outputs = metric(eval_data, predictions, scores)

        mean = np.mean(inst_outputs)
        sum = np.sum(inst_outputs)
        std = np.std(inst_outputs)
        # ci_lower, ci_upper = bootstrap.ci(inst_outputs)

        results.update({
            prefix + 'mean': mean,
            prefix + 'sum': sum,
            prefix + 'std': std,
            # prefix + 'ci_lower': ci_lower,
            # prefix + 'ci_upper': ci_upper,
        })

    config.dump_pretty(results, 'results.%sjson' % split_prefix)

    return results
