import sys
from nltk.metrics import distance
from nltk.translate import bleu_score
import matplotlib.pyplot as plt
import seaborn as sns


def main(experiment_name):
    results_dir_path = f'../results/{experiment_name}'
    preds_file_path = f'{results_dir_path}/predictions.txt'
    plot_losses_file_path = f'{results_dir_path}/plot_losses.txt'

    context_results = {}
    context_sizes = ['1 - 10', '11 - 20', '21 - 30', '30+']

    for context_size in context_sizes:
        context_results[context_size] = {
            'n_total': 0,
            'exact_match_total': 0,
            'precision_total': 0,
            'recall_total': 0,
        }

    edit_distance_total = 0
    bleu_references = []
    bleu_hypotheses = []

    with open(preds_file_path) as preds_file:
        lines = preds_file.readlines()

        for i in range(0, len(lines), 3):
            source = lines[i].rstrip()
            target = lines[i + 1].rstrip()
            pred = ' '.join(lines[i + 2].rstrip().split()[:-1])

            context_size = get_context_size(source)
            results = context_results[context_size]

            results['n_total'] += 1

            if target == pred:
                results['exact_match_total'] += 1

            target_tokens = target.split()
            pred_tokens = pred.split()

            results['precision_total'] += compute_precision(
                target_tokens, pred_tokens)
            results['recall_total'] += compute_recall(
                target_tokens, pred_tokens)

            edit_distance_total += compute_edit_distance(
                ''.join(target_tokens), ''.join(pred_tokens))

            bleu_references.append([target_tokens])
            bleu_hypotheses.append(pred_tokens)

    n_total = 0
    exact_match_total = 0
    precision_total = 0
    recall_total = 0

    context_precisions = []
    context_recalls = []
    context_f_scores = []

    for context_size in context_results:
        results = context_results[context_size]

        n_total += results['n_total']
        exact_match_total += results['exact_match_total']
        precision_total += results['precision_total']
        recall_total += results['recall_total']

        precision = results['precision_total'] / results['n_total']
        recall = results['recall_total'] / results['n_total']
        f_score = compute_f_score(precision, recall)

        context_precisions.append(precision)
        context_recalls.append(recall)
        context_f_scores.append(f_score)

    plot_metrics_vs_context_size(
        context_sizes, context_precisions, context_recalls, context_f_scores)

    exact_match = exact_match_total / n_total
    precision = precision_total / n_total
    recall = recall_total / n_total
    f_score = 2 * precision * recall / (precision + recall)
    edit_distance = edit_distance_total / n_total
    bleu = bleu_score.corpus_bleu(bleu_references, bleu_hypotheses)

    print(f'Total test examples: {n_total}')
    print(f'Exact match rate: {exact_match}')
    print(f'Precision: {precision}')
    print(f'Recall: {recall}')
    print(f'F-Score: {f_score}')
    print(f'Average edit distance: {edit_distance}')
    print(f'BLEU score: {bleu}')

    plot_losses = []

    with open(plot_losses_file_path) as plot_losses_file:
        for line in plot_losses_file.readlines():
            plot_losses.append(float(line))

    plot_training_losses(plot_losses)


def compute_precision(target_tokens, pred_tokens):
    if not pred_tokens:
        return 1
    count = 0
    for pred_token in pred_tokens:
        if pred_token in target_tokens:
            count += 1
    return count / len(pred_tokens)


def compute_recall(target_tokens, pred_tokens):
    if not target_tokens:
        return 1
    count = 0
    for target_token in target_tokens:
        if target_token in pred_tokens:
            count += 1
    return count / len(target_tokens)


def compute_f_score(precision, recall):
    return 2 * precision * recall / (precision + recall)


def compute_edit_distance(target, pred):
    return distance.edit_distance(target, pred) / max(len(target), len(pred))


def get_context_size(source):
    # Subtract 3 punctuation tokens
    size = len(source.split()) - 3

    if size <= 10:
        return '1 - 10'
    elif size <= 20:
        return '11 - 20'
    elif size <= 30:
        return '21 - 30'
    else:
        return '30+'


def plot_metrics_vs_context_size(
        context_sizes, context_precisions, context_recalls, context_f_scores):
    plt.figure(figsize=(8, 5))
    sns.set_theme()

    bar_x = context_sizes + context_sizes
    bar_y = context_precisions + context_recalls
    bar_hue = ['Precision'] * len(context_precisions) \
        + ['Recall'] * len(context_recalls)
    sns.barplot(x=bar_x, y=bar_y, hue=bar_hue, palette=['red', 'orange'])

    line_x = context_sizes
    line_y = context_f_scores
    line_hue = ['F-Score'] * len(context_f_scores)
    sns.lineplot(
        x=line_x, y=line_y, hue=line_hue, marker='o', palette=['blue'],
        linewidth=3)

    plt.title('Metrics vs. Context Size', fontsize='x-large')
    plt.tight_layout()
    plt.show()


def plot_training_losses(plot_losses):
    plt.figure(figsize=(8, 5))

    sns.lineplot(x=range(len(plot_losses)), y=plot_losses)

    plt.xlabel('Iterations (thousands)', size='large')
    plt.ylabel('Negative Log Likelihood Loss', size='large')
    plt.title('Training Losses', size='x-large')
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    experiment_name = sys.argv[1]
    main(experiment_name)
