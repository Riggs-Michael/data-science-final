import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


brackets = ["herald", "guardian", "crusader", "archon", "legend", "ancient", "divine", "immortal"]
toxicity_categories = ['No Toxicity', 'Low Toxicity', 'Mild Toxicity', 'Moderate Toxicity', 'Extreme Toxicity']


def create_toxicity_distribution_chart(bracket, df):
    categorical_toxicity = pd.Categorical(df['Toxicity'], categories=toxicity_categories, ordered=True)
    categorical_toxicity.value_counts().plot(kind='bar')
    plt.title(f'{bracket.capitalize()} Toxicity Distribution')
    plt.xticks(rotation=10)
    plt.savefig(f'{bracket}_toxicity_distribution.png', bbox_inches='tight', dpi=300)


if __name__ == '__main__':
    processed_dfs = []
    processed_stats = []
    for bracket in brackets:
        df = pd.read_csv(f'labeled_{bracket}_match_transcripts.csv')
        unclassified = df.query('`Toxicity Ranking` < 1 & Transcript')
        unclassified_count = len(unclassified)
        df.drop(unclassified.index, inplace=True)
        no_chat = df.query('`Toxicity Ranking` < 1')
        no_chat_unclassified_count = len(no_chat)
        df['Toxicity'].replace('Undetermined', 'No Toxicity', inplace=True)
        df['Toxicity Ranking'].replace(0, 1, inplace=True)
        create_toxicity_distribution_chart(bracket, df)
        processed_dfs.append(df)
        stats = df['Toxicity Ranking'].describe()[['mean', 'std', '50%']].to_frame().T
        stats.insert(len(stats.columns), column='Removed Match Count', value=unclassified_count)
        stats.insert(len(stats.columns), column='No Chat Count', value=no_chat_unclassified_count)
        processed_stats.append(stats)
    all_stats = pd.concat(processed_stats)
    all_stats.insert(0, 'Bracket', brackets)
    all_stats.to_csv('toxicity_stats.csv', index=False)
    all_brackets_df = pd.concat(processed_dfs, axis=0, keys=brackets).reset_index()
    all_brackets_df.columns = ['Bracket', 'Index', 'Match Id', 'Transcript', 'Toxicity', 'Toxicity Ranking']
    all_brackets_df['Bracket'] = pd.Categorical(all_brackets_df['Bracket'], categories=brackets, ordered=True)
    all_brackets_df = all_brackets_df.sort_values('Bracket')
    plt.figure(figsize=(12, 8))
    boxplot = sns.boxplot(x='Bracket', y='Toxicity Ranking', data=all_brackets_df, showmeans=True)
    boxplot.set_title('Toxicity Ranking by Bracket', fontsize=16)
    boxplot.set_xlabel('Bracket', fontsize=14)
    boxplot.set_ylabel('Toxicity Ranking', fontsize=14)
    plt.savefig('toxicity_boxplot.png', bbox_inches='tight', dpi=300)
