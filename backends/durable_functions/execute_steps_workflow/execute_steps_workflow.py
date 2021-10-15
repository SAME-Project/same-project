from .context import Step
import logging
import azure.durable_functions as df


EXECUTE_STEP_ACTIVITY_NAME = "execute_step"


def _execute_steps_workflow(context: df.DurableOrchestrationContext):
    """
    Orchestrates the execution of a given list of Steps.
    """
    # Unpack inputs
    input = context.get_input()
    if input is None:
        raise Exception("Input not provided")
    
    # Get user for which to execute (and get/put state)
    user = input.get("user", None)
    if user is None:
        raise Exception("User not provided")

    # Get all Steps to execute
    steps_json_list = input.get("steps", None)
    if steps_json_list is None:
        raise Exception("Steps not provided")

    # Deserialize Steps
    steps = Step.from_json_list(steps_json_list)
    num_steps = len(steps)
    logging.info(f"Got {num_steps} steps to execute")

    # Get start state (optional) provided by the caller (default: 0)
    # TODO: Add unit test to resume from non-zero ID
    id = input.get("idin", 0)

    # TODO Determine which ones can be executed in parallel and construct the appropriate DAG
    # executions = []
    # for step in steps:
    #     execution = context.call_activity(EXECUTE_STEP_ACTIVITY_NAME, step)
    #     executions.append(execution)
    # results = yield context.task_all(executions)

    # Execute all steps one after the other
    # Note: Assuming that the list of steps is in order of required (sequential) execution
    results = []
    for step in steps:
        idin = id
        idout = id + 1
        id += 1
        input  = {
            "step": step,
            "user": user,
            "idin": idin,
            "idout": idout,
        }
        result = yield context.call_activity(EXECUTE_STEP_ACTIVITY_NAME, input)
        results.append(result)

    return results


execute_steps_workflow = df.Orchestrator.create(_execute_steps_workflow)
