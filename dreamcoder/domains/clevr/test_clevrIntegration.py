"""
Integration tests for clevr/main.py | Author : Catherine Wong.

These are full integration tests for the functionality of the various components
of a DreamCoder iteration using the CLEVR dataset, essentially moving 'chronologically'
through an iteration.

All tests are manually added to a 'test_all' function.
"""
from dreamcoder.utilities import DEFAULT_OUTPUT_DIRECTORY, pop_all_domain_specific_args
from dreamcoder.dreamcoder import ecIterator
import inspect
import os

def set_default_args(args):
    """Helper function to set default arguments in the args dictionary."""
    args['contextual'] = True
    args['biasOptimal'] = True
    args['taskBatchSize'] = 10

def test_clevr_specific_command_line_args(DOMAIN_SPECIFIC_ARGS, args):
    """
    Test that we correctly use and remove all CLEVR-specific command line arguments.
    """
    # We have to pop off all domain-specific arguments here, or we'll not have the 
    # argument to actually run the intergration test.
    pop_all_domain_specific_args(args_dict=args, iterator_fn=ecIterator)
    # Check that we've removed any arguments that aren't present in the ecIterator.
    ecIterator_parameters = inspect.signature(ecIterator).parameters
    for arg in DOMAIN_SPECIFIC_ARGS:
        assert arg in ecIterator_parameters
    for arg in args:
        assert arg in ecIterator_parameters
    # Integration checks on the actual parameters.
    assert len(DOMAIN_SPECIFIC_ARGS["tasks"]) > 0
    assert len(DOMAIN_SPECIFIC_ARGS["testingTasks"]) > 0
    assert "1_zero_hop" in DOMAIN_SPECIFIC_ARGS["languageDataset"]
    assert "2_transform" in DOMAIN_SPECIFIC_ARGS["languageDataset"]
    assert len(DOMAIN_SPECIFIC_ARGS["grammar"]) > 0
    # Check that the output prefix was created.
    checkpoint_dir =os.path.dirname(DOMAIN_SPECIFIC_ARGS["outputPrefix"])
    assert os.path.isdir(checkpoint_dir)
    assert args["iterations"] > 1

def test_integration_task_language_synthetic(DOMAIN_SPECIFIC_ARGS, args):
    """Test that we correctly load all synthetic language for all CLEVR tasks"""
    pop_all_domain_specific_args(args_dict=args, iterator_fn=ecIterator)
    args['enumerationTimeout'] = 0
    generator = ecIterator(**DOMAIN_SPECIFIC_ARGS, **args,
     test_task_language=True)
    
    for current_ec_result in generator:
        language_for_tasks, vocabularies = current_ec_result.taskLanguage, current_ec_result.vocabularies
        break
        
    assert len(vocabularies['train']) > 0
    assert len(vocabularies['test']) > 0
    
    # Check that all of the tasks have language.
    for task in DOMAIN_SPECIFIC_ARGS['tasks']:
        assert task.name in language_for_tasks
        assert len(language_for_tasks) > 0
        
    for task in DOMAIN_SPECIFIC_ARGS['testingTasks']:
        assert task.name in language_for_tasks
        assert len(language_for_tasks) > 0

def test_integration_background_helmholtz_bootstrap_primitives(DOMAIN_SPECIFIC_ARGS, args):
    """Test that we successfully retrieve Helmholtz frontiers during the initial background
    Helmholtz enumeration using the bootstrap primitives as our starting grammar.
    """
    pop_all_domain_specific_args(args_dict=args, iterator_fn=ecIterator)
    set_default_args(args)
    args['enumerationTimeout'] = 2.0
    
    generator = ecIterator(**DOMAIN_SPECIFIC_ARGS, **args,
     test_background_helmholtz=True)
    helmholtz_frontiers_fn = next(generator)
    helmholtz_frontiers = helmholtz_frontiers()
    assert len(helmholtz_frontiers) > 0

def test_wake_generative_bootstrap_primitives(DOMAIN_SPECIFIC_ARGS, args):
    """Test that we can successfully run a round of top-down enumeration."""
    pop_all_domain_specific_args(args_dict=args, iterator_fn=ecIterator)
    set_default_args(args)
    args['enumerationTimeout'] = 2.0
    generator = ecIterator(**DOMAIN_SPECIFIC_ARGS, **args,
     test_wake_generative_enumeration=True)
    result = next(generator)
    assert len(result.tasksAttempted) == args['taskBatchSize']
    found_frontier = False
    for task in DOMAIN_SPECIFIC_ARGS['tasks']:
        assert task in result.allFrontiers
        if not result.allFrontiers[task].empty: found_frontier = True
    assert found_frontier

def test_sleep_recognition_round_0_no_language_bootstrap_primitives(DOMAIN_SPECIFIC_ARGS, args):
    """Test that we can successfully train and enumerate using a no-language recognizer."""
    pop_all_domain_specific_args(args_dict=args, iterator_fn=ecIterator)
    set_default_args(args)
    args['enumerationTimeout'] = 2.0
    args['recognitionSteps'] = 100
    generator = ecIterator(**DOMAIN_SPECIFIC_ARGS, **args,
     test_sleep_recognition_0=True)
    result = next(generator)
    
    found_frontier = False
    for task in DOMAIN_SPECIFIC_ARGS['tasks']:
        assert task in result.allFrontiers
        if not result.allFrontiers[task].empty: found_frontier = True
    assert found_frontier

def test_sleep_recognition_round_0_helmholtz_only_bootstrap_primitives(DOMAIN_SPECIFIC_ARGS, args):
    """Test that we can successfully train and enumerate using a no-language recognizer with only Helmholtz entries."""
    pop_all_domain_specific_args(args_dict=args, iterator_fn=ecIterator)
    set_default_args(args)
    args['enumerationTimeout'] = 2.0
    args['recognitionSteps'] = 100
    args['helmholtzRatio'] = 1.0
    generator = ecIterator(**DOMAIN_SPECIFIC_ARGS, **args,
     test_sleep_recognition_0=True)
    result = next(generator)
    
    found_frontier = False
    for task in DOMAIN_SPECIFIC_ARGS['tasks']:
        assert task in result.allFrontiers
        if not result.allFrontiers[task].empty: found_frontier = True
    assert found_frontier

def test_sleep_recognition_round_1_with_language_bootstrap_primitives(DOMAIN_SPECIFIC_ARGS, args):
    """Test that we can successfully train and enumerate using a with-language recognizer."""
    pop_all_domain_specific_args(args_dict=args, iterator_fn=ecIterator)
    set_default_args(args)
    args['enumerationTimeout'] = 2.0
    args['recognitionSteps'] = 50
    args['recognition_0'] = []
    args['recognition_1'] = ["examples", "language"]
    args['language_encoder'] = 'recurrent'
    args['synchronous_grammar'] = True
    args['moses_dir'] = './moses_compiled'
    args['smt_phrase_length'] = 1
    generator = ecIterator(**DOMAIN_SPECIFIC_ARGS, **args,
     test_sleep_recognition_1=True)
    result = next(generator)
    
    found_frontier = False
    for task in DOMAIN_SPECIFIC_ARGS['tasks']:
        assert task in result.allFrontiers
        if not result.allFrontiers[task].empty: found_frontier = True
    assert found_frontier

def test_integration_consolidation_no_language_original_primitives(DOMAIN_SPECIFIC_ARGS, args):
    """Integration test that we can run through a round of consolidation completely.
    Note that running this test requires setting the primitives at the command line to
    --primitives clevr_original clevr_map_transform
    """
    pop_all_domain_specific_args(args_dict=args, iterator_fn=ecIterator)
    set_default_args(args)
    args['enumerationTimeout'] = 2.0
    args['recognitionSteps'] = 50
    args['helmholtzRatio'] = 1.0
    args['taskBatchSize'] = 30
    generator = ecIterator(**DOMAIN_SPECIFIC_ARGS, **args) # We naturally return the result after consolidation; no flag is needed.
    result = next(generator)
    
    assert len(result.grammars) == 2 
    
def test_consolidation_no_language_bootstrap_primitives(DOMAIN_SPECIFIC_ARGS, args):
    """Test that we can successfully run a consolidation round with bootstrapped primitives."""
    pop_all_domain_specific_args(args_dict=args, iterator_fn=ecIterator)
    set_default_args(args)
    args['enumerationTimeout'] = 2.0
    args['recognitionSteps'] = 50
    args['helmholtzRatio'] = 1.0
    args['taskBatchSize'] = 30
    generator = ecIterator(**DOMAIN_SPECIFIC_ARGS, **args) # We naturally return the result after consolidation; no flag is needed.
    result = next(generator)
    
    assert len(result.grammars) == 2 

def test_integration_next_iteration_discovered_primitives_original_primitives(DOMAIN_SPECIFIC_ARGS, args):
    """Integration test using the original primitives to determine that we can run a second round with new primitives in the grammar.
    Note that running this test requires setting the primitives at the command line to
    --primitives clevr_original clevr_map_transform
    """
    pop_all_domain_specific_args(args_dict=args, iterator_fn=ecIterator)
    set_default_args(args)
    args['testingTimeout'] = 0.5
    args['enumerationTimeout'] = 2.0
    args['recognitionSteps'] = 50
    args['helmholtzRatio'] = 1.0
    args['taskBatchSize'] = 30
    generator = ecIterator(**DOMAIN_SPECIFIC_ARGS, **args) # We naturally return the result after consolidation; no flag is needed.
    _ = next(generator)
    result = next(generator)
    
    assert len(result.grammars) == 3
    found_frontier = False
    for task in DOMAIN_SPECIFIC_ARGS['tasks']:
        assert task in result.allFrontiers
        if not result.allFrontiers[task].empty: found_frontier = True
    assert found_frontier

def test_integration_next_iteration_language_bootstrap_primitives(DOMAIN_SPECIFIC_ARGS, args):
    """
    Integration tests the appropriate settings on the next iteration when we have language in the loop."""
    pass

def run_test(test_fn, DOMAIN_SPECIFIC_ARGS, args):
    """Utility function for running tests"""
    print(f"Running {test_fn.__name__}...")
    test_fn(DOMAIN_SPECIFIC_ARGS, args)
    print("\n")

def test_all(DOMAIN_SPECIFIC_ARGS, args):
    print("Running tests for clevrIntegration.py...")
    # run_test(test_clevr_specific_command_line_args, DOMAIN_SPECIFIC_ARGS, args)
    # run_test(test_integration_task_language_synthetic, DOMAIN_SPECIFIC_ARGS, args)
    # run_test(test_integration_background_helmholtz_bootstrap_primitives, DOMAIN_SPECIFIC_ARGS, args)
    # run_test(test_wake_generative_bootstrap_primitives, DOMAIN_SPECIFIC_ARGS, args)
    # run_test(test_sleep_recognition_round_0_no_language_bootstrap_primitives, DOMAIN_SPECIFIC_ARGS, args)
    # run_test(test_sleep_recognition_round_0_helmholtz_only_bootstrap_primitives, DOMAIN_SPECIFIC_ARGS, args)
    run_test(test_sleep_recognition_round_1_with_language_bootstrap_primitives,DOMAIN_SPECIFIC_ARGS, args)
    # run_test(test_integration_consolidation_no_language_original_primitives,DOMAIN_SPECIFIC_ARGS, args) # Requires setting primitives at command line.
    # run_test(test_integration_next_iteration_discovered_primitives_original_primitives,DOMAIN_SPECIFIC_ARGS, args)  # Requires setting primitives at command line.
    # run_test(test_next_iteration_settings_random_shuffle_and_annealing, DOMAIN_SPECIFIC_ARGS, args)
    print(".....finished running all tests!")