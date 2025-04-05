from pprint import pprint
from src.profile.Malcolm2025Profile import Malcolm2025Profile
# from .JobPipelineController import JobPipelineController


if __name__ == "__main__":
  profile_creator = Malcolm2025Profile()
  profile = profile_creator.create_profile()
  pprint(vars(profile), depth=4, width=120)
  # controller = JobPipelineController(profile_creator=profile_creator)
  # controller.run_pipeline("Seattle")
  # print(profile)