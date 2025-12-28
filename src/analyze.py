import pandas as pd
import numpy as np
from scipy import stats

# ============================================================================
# DATA PREPARATION
# ============================================================================

def prepare_possession_data(synced_df):
    """
    Extract and prepare possession and passing option data.
    
    Parameters:
    -----------
    synced_df : pd.DataFrame
        The synced dataframe containing all event types
    
    Returns:
    --------
    tuple: (possessions, passing_options)
    """
    possessions = synced_df[synced_df['event_type'] == 'player_possession'].copy()
    passing_options = synced_df[synced_df['event_type'] == 'passing_option'].copy()
    
    print(f"Extracted {len(possessions)} possessions and {len(passing_options)} passing options")
    return possessions, passing_options


def link_runs_to_possessions(possessions, passing_options):
    """
    Link passing options (runs) to their parent possession events.
    
    Parameters:
    -----------
    possessions : pd.DataFrame
        Possession events
    passing_options : pd.DataFrame
        Passing option/run events
    
    Returns:
    --------
    pd.DataFrame: Possessions enriched with run aggregations
    """
    if 'associated_player_possession_event_id' not in passing_options.columns:
        print("Cannot find linking column - checking alternatives...")
        print(passing_options.columns[passing_options.columns.str.contains('event_id')].tolist())
        return possessions
    
    # Link runs to possessions
    passing_options['parent_possession_id'] = passing_options['associated_player_possession_event_id']
    
    # Aggregate run statistics per possession
    run_summary = passing_options.groupby('parent_possession_id').agg({
        'dangerous': ['sum', 'max'],
        'xthreat': ['mean', 'max', 'sum'],
        'targeted': 'sum',
        'player_name': 'count'
    }).reset_index()
    
    run_summary.columns = ['possession_id', 'n_dangerous_runs', 'any_dangerous_run',
                           'avg_xthreat', 'max_xthreat', 'total_xthreat', 
                           'n_targeted_runs', 'n_total_runs']
    
    # Merge back to possessions
    possessions_with_runs = possessions.merge(
        run_summary, 
        left_on='event_id', 
        right_on='possession_id', 
        how='left'
    )
    
    # Calculate untargeted dangerous runs
    possessions_with_runs['n_untargeted_dangerous'] = (
        possessions_with_runs['n_dangerous_runs'] - 
        possessions_with_runs['n_targeted_runs'].fillna(0)
    )
    
    print(f"Successfully linked {len(run_summary)} possessions to their runs")
    return possessions_with_runs


# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def analyze_run_impact(possessions_with_runs):
    """
    Analyze how dangerous runs impact possession outcomes.
    
    Parameters:
    -----------
    possessions_with_runs : pd.DataFrame
        Possessions with run statistics
    """
    print("\n" + "="*80)
    print("POSSESSION OUTCOMES BY RUN CHARACTERISTICS")
    print("="*80)
    
    poss_with_runs = possessions_with_runs[possessions_with_runs['n_total_runs'] > 0]
    
    print(f"\nPossessions with at least 1 dangerous run: {(poss_with_runs['any_dangerous_run'] > 0).sum()}")
    print(f"Possessions with untargeted dangerous runs: {(poss_with_runs['n_untargeted_dangerous'] > 0).sum()}")
    
    # Analyze outcomes by run quality
    outcome_cols = ['pass_outcome', 'lead_to_shot', 'lead_to_goal', 'xthreat', 'forward_momentum']
    outcome_cols = [c for c in outcome_cols if c in possessions_with_runs.columns]
    
    if outcome_cols:
        print("\n--- Comparing possessions WITH vs WITHOUT dangerous runs ---")
        
        has_dangerous = poss_with_runs[poss_with_runs['any_dangerous_run'] > 0]
        no_dangerous = poss_with_runs[poss_with_runs['any_dangerous_run'] == 0]
        
        for col in outcome_cols:
            if possessions_with_runs[col].dtype in ['float64', 'int64']:
                print(f"\n{col}:")
                print(f"  With dangerous run: {has_dangerous[col].mean():.3f}")
                print(f"  Without dangerous run: {no_dangerous[col].mean():.3f}")
            elif col == 'pass_outcome':
                print(f"\n{col} distribution:")
                print("With dangerous runs:")
                print(has_dangerous[col].value_counts(normalize=True).head(3))


def analyze_untargeted_runs(possessions_with_runs):
    """
    Analyze the value of untargeted (ignored) dangerous runs.
    
    Parameters:
    -----------
    possessions_with_runs : pd.DataFrame
        Possessions with run statistics
    """
    print("\n" + "="*80)
    print("UNTARGETED RUN VALUE HYPOTHESIS")
    print("="*80)
    
    poss_with_runs = possessions_with_runs[possessions_with_runs['n_total_runs'] > 0]
    
    targeted_dangerous = poss_with_runs[
        (poss_with_runs['n_dangerous_runs'] > 0) & 
        (poss_with_runs['n_targeted_runs'] > 0)
    ]
    
    ignored_dangerous = poss_with_runs[
        (poss_with_runs['n_dangerous_runs'] > 0) & 
        (poss_with_runs['n_targeted_runs'] == 0)
    ]
    
    print(f"\nPossessions where dangerous run WAS targeted: {len(targeted_dangerous)}")
    print(f"Possessions where dangerous run was IGNORED: {len(ignored_dangerous)}")
    
    if len(targeted_dangerous) > 0 and len(ignored_dangerous) > 0:
        print("\nDid ignoring the dangerous run hurt the outcome?")
        
        for col in ['xthreat', 'pass_outcome', 'lead_to_shot']:
            if col in possessions_with_runs.columns and col in ['xthreat']:
                t_val = targeted_dangerous[col].mean()
                i_val = ignored_dangerous[col].mean()
                print(f"  {col}: Targeted={t_val:.3f}, Ignored={i_val:.3f}, Diff={t_val-i_val:.3f}")
    
    return targeted_dangerous, ignored_dangerous


def analyze_defensive_impact(possessions_with_runs, ignored_dangerous):
    """
    Analyze whether untargeted runs created defensive space.
    
    Parameters:
    -----------
    possessions_with_runs : pd.DataFrame
        Possessions with run statistics
    ignored_dangerous : pd.DataFrame
        Possessions where dangerous runs were ignored
    """
    print("\n" + "="*80)
    print("DEFENSIVE IMPACT - DID RUNS CREATE SPACE?")
    print("="*80)
    
    defensive_cols = ['n_opponents_ahead_start', 'n_opponents_ahead_end', 
                      'separation_start', 'separation_end', 'separation_gain']
    defensive_cols = [c for c in defensive_cols if c in possessions_with_runs.columns]
    
    if defensive_cols and len(ignored_dangerous) > 0:
        print("\nDefensive metrics when dangerous runs were ignored:")
        for col in defensive_cols:
            print(f"  {col}: {ignored_dangerous[col].mean():.2f}")
        
        print("\nDid the actual pass benefit from the decoy run?")
        if 'separation_gain' in possessions_with_runs.columns:
            print(f"  Avg separation gained: {ignored_dangerous['separation_gain'].mean():.2f}")


def compare_with_vs_without_runs(possessions):
    """
    Compare possessions with runs vs without runs across multiple metrics.
    
    Parameters:
    -----------
    possessions : pd.DataFrame
        All possession events
    
    Returns:
    --------
    dict: Results of comparison analysis
    """
    print("\n" + "="*80)
    print("RUN VALUE ADDED (RVA) METRIC DEVELOPMENT")
    print("="*80)
    
    # Split possessions
    poss_no_runs = possessions[possessions['n_off_ball_runs'] == 0].copy()
    poss_with_runs = possessions[possessions['n_off_ball_runs'] > 0].copy()
    
    print(f"\nPossessions without runs: {len(poss_no_runs)}")
    print(f"Possessions with runs: {len(poss_with_runs)}")
    
    # Define outcome metrics
    outcomes = {
        'pass_success': lambda x: (x['pass_outcome'] == 'successful').astype(float) if 'pass_outcome' in x.columns else None,
        'progression': lambda x: x['delta_to_last_defensive_line_gain'] if 'delta_to_last_defensive_line_gain' in x.columns else None,
        'separation_gained': lambda x: x['separation_gain'] if 'separation_gain' in x.columns else None,
        'lead_to_shot': lambda x: x['lead_to_shot'].fillna(0) if 'lead_to_shot' in x.columns else None,
    }
    
    print("\n" + "="*80)
    print("IMPACT ANALYSIS: WITH RUNS vs WITHOUT RUNS")
    print("="*80)
    
    results = {}
    for metric_name, metric_func in outcomes.items():
        with_runs_metric = metric_func(poss_with_runs)
        without_runs_metric = metric_func(poss_no_runs)
        
        if with_runs_metric is not None and without_runs_metric is not None:
            with_runs_metric = with_runs_metric.dropna()
            without_runs_metric = without_runs_metric.dropna()
            
            if len(with_runs_metric) > 0 and len(without_runs_metric) > 0:
                mean_with = with_runs_metric.mean()
                mean_without = without_runs_metric.mean()
                diff = mean_with - mean_without
                
                # Statistical test
                if len(with_runs_metric) > 20 and len(without_runs_metric) > 20:
                    t_stat, p_val = stats.ttest_ind(with_runs_metric, without_runs_metric)
                    sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
                else:
                    p_val, sig = None, ""
                
                results[metric_name] = {
                    'with_runs': mean_with,
                    'without_runs': mean_without,
                    'difference': diff,
                    'p_value': p_val
                }
                
                print(f"\n{metric_name.upper()}:")
                print(f"  With runs: {mean_with:.3f}")
                print(f"  Without runs: {mean_without:.3f}")
                print(f"  Difference: {diff:+.3f} {sig}")
                if p_val:
                    print(f"  p-value: {p_val:.4f}")
    
    return results


def analyze_run_characteristics(possessions, passing_options):
    """
    Analyze which run characteristics correlate with better outcomes.
    
    Parameters:
    -----------
    possessions : pd.DataFrame
        Possession events
    passing_options : pd.DataFrame
        Passing option events
    
    Returns:
    --------
    pd.DataFrame: Possessions enriched with run features
    """
    print("\n" + "="*80)
    print("RUN CHARACTERISTICS & VALUE")
    print("="*80)
    
    poss_with_runs = possessions[possessions['n_off_ball_runs'] > 0].copy()
    passing_options['parent_possession_id'] = passing_options['associated_player_possession_event_id']
    
    # Aggregate run features
    run_features = passing_options.groupby('parent_possession_id').agg({
        'dangerous': 'sum',
        'xthreat': ['mean', 'max'],
        'n_simultaneous_runs': 'max',
        'distance_to_player_in_possession_start': 'mean',
        'player_name': 'count'
    }).reset_index()
    
    run_features.columns = ['possession_id', 'n_dangerous', 'avg_xthreat_runs', 
                            'max_xthreat_run', 'max_simultaneous', 'avg_distance', 'n_runs']
    
    poss_enriched = poss_with_runs.merge(
        run_features, 
        left_on='event_id', 
        right_on='possession_id', 
        how='left'
    )
    
    # Define outcomes
    outcomes = {
        'pass_success': lambda x: (x['pass_outcome'] == 'successful').astype(float) if 'pass_outcome' in x.columns else None,
        'progression': lambda x: x['delta_to_last_defensive_line_gain'] if 'delta_to_last_defensive_line_gain' in x.columns else None,
        'separation_gained': lambda x: x['separation_gain'] if 'separation_gain' in x.columns else None,
    }
    
    print("\nRun characteristics that improve outcomes:")
    
    for outcome_name, outcome_func in outcomes.items():
        outcome_vals = outcome_func(poss_enriched)
        if outcome_vals is not None:
            outcome_vals = outcome_vals.dropna()
            
            print(f"\n{outcome_name.upper()}:")
            for feature in ['n_dangerous', 'max_simultaneous', 'n_runs']:
                if feature in poss_enriched.columns:
                    corr = poss_enriched[feature].corr(outcome_vals)
                    if not np.isnan(corr):
                        print(f"  Correlation with {feature}: {corr:.3f}")
    
    return poss_enriched


def calculate_run_value_added(passing_options, possessions):
    """
    Calculate Run Value Added (RVA) for each run - EVIDENCE-BASED VERSION v2.
    
    Based on empirical findings:
    - Targeted runs lose LESS space than ignored runs (-2.00m vs -2.45m)
    - Runs create +77% more shots but same goals (volume not quality)
    - Decoy runs have NEGATIVE value (cause hesitation/space loss)
    - Shot creation is the main benefit, but only when the run is used
    
    KEY FIX: Shot credit only given to TARGETED dangerous runs (not ignored ones)
    
    Parameters:
    -----------
    passing_options : pd.DataFrame
        Passing option events
    possessions : pd.DataFrame
        Possession events
    
    Returns:
    --------
    pd.DataFrame: Passing options with RVA calculated
    """
    print("\n" + "="*80)
    print("RUN VALUE ADDED (RVA) FORMULA - EVIDENCE-BASED V2")
    print("="*80)
    
    print("\nRVA components based on empirical findings:")
    print("1. Shot Creation Value: Only credited to TARGETED dangerous runs")
    print("2. Direct Threat Value: xThreat * completion when targeted")
    print("3. Progression Value: Helps advance play (+0.225m per possession)")
    print("4. Decoy Penalty: Ignored dangerous runs LOSE shot credit + penalty")
    print("5. Simultaneous Run Bonus: Multiple runs stress defense more")
    
    # Merge with possession outcomes
    passing_options_merged = passing_options.merge(
        possessions[['event_id', 'pass_outcome', 'separation_gain', 'lead_to_shot']],
        left_on='parent_possession_id',
        right_on='event_id',
        how='left',
        suffixes=('', '_poss')
    )
    
    # 1. SHOT CREATION VALUE - FIXED VERSION
    # Only credit shot creation if the dangerous run was TARGETED
    # Ignored dangerous runs don't get shot credit (they didn't contribute to the shot)
    shot_created = passing_options_merged['lead_to_shot'].fillna(0)
    
    passing_options_merged['shot_value'] = np.where(
        (passing_options_merged['dangerous'] == 1) & (passing_options_merged['targeted'] == 1),
        passing_options_merged['xthreat'] * shot_created * 2.5,  # Full credit if targeted
        np.where(
            passing_options_merged['dangerous'] == 1,
            passing_options_merged['xthreat'] * shot_created * 0.3,  # Minimal credit if ignored
            0
        )
    )
    
    # 2. DIRECT THREAT VALUE (when targeted)
    # Only credit runs that are actually used
    passing_options_merged['direct_value'] = np.where(
        passing_options_merged['targeted'] == 1,
        passing_options_merged['xthreat'] * passing_options_merged['xpass_completion'],
        0
    )
    
    # 3. PROGRESSION VALUE 
    # Runs help advance +0.225m per possession with runs
    # All dangerous runs contribute to progression (even if not targeted)
    passing_options_merged['progression_value'] = np.where(
        passing_options_merged['dangerous'] == 1,
        passing_options_merged['xthreat'] * 0.12,  
        0
    )
    
    # 4. DECOY PENALTY - STRENGTHENED
    # Ignored dangerous runs lose 0.45m more space AND don't create shots
    passing_options_merged['decoy_penalty'] = np.where(
        (passing_options_merged['targeted'] == 0) & 
        (passing_options_merged['dangerous'] == 1),
        passing_options_merged['xthreat'] * -0.25,  
        0
    )
    
    # 5. SIMULTANEOUS RUN BONUS (when multiple runs stress defense)
    passing_options_merged['overload_value'] = np.where(
        (passing_options_merged['n_simultaneous_runs'] > 1) & 
        (passing_options_merged['dangerous'] == 1),
        passing_options_merged['xthreat'] * 0.08 * passing_options_merged['n_simultaneous_runs'],
        0
    )
    
    # TOTAL RVA
    passing_options_merged['RVA'] = (
        passing_options_merged['shot_value'] +           # Primary value (conditional)
        passing_options_merged['direct_value'] +         # When targeted
        passing_options_merged['progression_value'] +    # Field advancement
        passing_options_merged['decoy_penalty'] +        # Penalty for ignored runs
        passing_options_merged['overload_value']         # Multiple simultaneous runs
    )
    
    return passing_options_merged


def summarize_rva(passing_options_with_rva):
    """
    Generate summary statistics and rankings for RVA.
    
    Parameters:
    -----------
    passing_options_with_rva : pd.DataFrame
        Passing options with RVA calculated
    
    Returns:
    --------
    pd.DataFrame: Player-level RVA rankings
    """
    print("\n" + "="*80)
    print("RVA SUMMARY STATISTICS")
    print("="*80)
    
    print(f"\nAverage RVA per run: {passing_options_with_rva['RVA'].mean():.4f}")
    print(f"Average RVA (targeted): {passing_options_with_rva[passing_options_with_rva['targeted']==1]['RVA'].mean():.4f}")
    print(f"Average RVA (untargeted): {passing_options_with_rva[passing_options_with_rva['targeted']==0]['RVA'].mean():.4f}")
    
    untargeted_dangerous = (passing_options_with_rva['targeted']==0) & (passing_options_with_rva['dangerous']==1)
    if untargeted_dangerous.sum() > 0:
        print(f"Average RVA (untargeted dangerous): {passing_options_with_rva[untargeted_dangerous]['RVA'].mean():.4f}")
    
    # Component breakdown
    print("\n--- RVA Component Breakdown ---")
    for component in ['shot_value', 'direct_value', 'progression_value', 'decoy_penalty', 'overload_value']:
        if component in passing_options_with_rva.columns:
            print(f"{component}: {passing_options_with_rva[component].mean():.4f}")
    
    # Top value creators
    print("\n" + "="*80)
    print("TOP RUN VALUE CREATORS (by total RVA)")
    print("="*80)
    
    player_rva = passing_options_with_rva.groupby('player_name').agg({
        'RVA': ['sum', 'mean', 'count'],
        'targeted': 'sum',
        'dangerous': 'sum',
        'shot_value': 'sum',
        'direct_value': 'sum'
    }).round(4)
    
    player_rva.columns = ['total_RVA', 'avg_RVA', 'n_runs', 'n_targeted', 'n_dangerous', 
                          'shot_contribution', 'direct_contribution']
    player_rva = player_rva.sort_values('total_RVA', ascending=False)
    
    print(player_rva.head(10))
    
    return player_rva
