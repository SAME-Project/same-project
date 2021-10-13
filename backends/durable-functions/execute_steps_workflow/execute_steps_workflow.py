from .context import Step
import logging
import azure.durable_functions as df


EXECUTE_STEP_ACTIVITY_NAME = "execute_step"


def _execute_steps_workflow(context: df.DurableOrchestrationContext):
    """
    Orchestrates the execution of a given list of Steps.
    """
    # Get all steps to execute
    input = context.get_input()
    steps_json_list = input["steps"]
    steps = Step.from_json_list(steps_json_list)
    
    user = input["user"]

    num_steps = len(steps)
    logging.info(f"Got {num_steps} steps to execute")

    # TODO Determine which ones can be executed in parallel and construct the appropriate DAG
    # executions = []
    # for step in steps:
    #     execution = context.call_activity(EXECUTE_STEP_ACTIVITY_NAME, step)
    #     executions.append(execution)
    # results = yield context.task_all(executions)

    # Execute all steps one after the other
    # Note: Assume that the list of steps is in order of required (sequential) execution
    results = []
    id = 0
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
