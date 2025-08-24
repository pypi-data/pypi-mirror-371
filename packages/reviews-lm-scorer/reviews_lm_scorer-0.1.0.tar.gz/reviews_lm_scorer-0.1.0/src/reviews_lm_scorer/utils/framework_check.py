
def framework_check(framework:str) -> None:
    if not isinstance(framework, str):
        raise ValueError(f"Invalid input type of {type(framework)}. framework_check function only accepts strings.")

    if framework.lower() == "torch":
        try:
            import torch
        except ImportError:
            raise ImportError(
                "PyTorch is required. Install PyTorch with 'pip install torch'."
            )
    else:
        raise ValueError(f"{framework} is not a supported framework")
