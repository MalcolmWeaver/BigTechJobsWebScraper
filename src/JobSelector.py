from src.storage.JobStorageInterface import JobStorageInterface
import requests
import structlog

logger = structlog.get_logger(__name__)

class JobSelector:
    def __init__(self, storage: JobStorageInterface):
        self.storage = storage

    def select_suitable_jobs(self, user_profile):
        jobs = self.storage.get_jobs(filters={"match_reason": None, "description": True})
        suitable_jobs = []
        for job in jobs:
            print(f"DEBUG: {job["posting_url"]}")
            llm_is_suitable = self.llm_is_suitable(job, user_profile)
            if llm_is_suitable:
                job["is_match"] = True
                # llm_created_cvs = self.llm_create_cvs(job, user_profile)
                # job.generated_cv = llm_created_cvs

            else:
                job["is_match"] = False

        return suitable_jobs

    def llm_is_suitable(self, job, user_profile):
        # NOTE: You need to have Ollama running in the background
        # Start it with: ollama serve (it runs by default on localhost:11434)
        try:
            # Define which model to use - ensure you've pulled it with: ollama pull llama2
            # Other good options: mistral, llama2:13b, or llama2-uncensored
            model_name = "llama2:13b"

            # Create a prompt that frames the evaluation task
            prompt = f"""
            Given the following, address the following questions:
            - Does the candidate address the qualifications? If there are preferred qualifications, would the candidate be competitive?
            - Do the candidates experience and education match the requirements? Ie. is it a coding role?
            - Would the candidate be competitive for the role?
            - Focus only on the measurable aspects of the job posting such as required years of experience, not on subjective aspects such as "strong problem-solving skills"

            JOB TITLE:
            {job["title"]}
            JOB DESCRIPTION:
            {job["description"]}
            JOB QUALIFICATIONS:
            {job["all_qualifications"]}
            JOB RESPONSIBILITIES:
            {job["responsibilities"]}

            APPLICANT PROFILE:
            Education: {user_profile.degree if hasattr(user_profile, 'degree') else 'Not specified'}
            Years of Experience: {user_profile.years_of_experience if hasattr(user_profile, 'years_of_experience') else 'Not specified'} years
            Resume: {user_profile.resume_text if hasattr(user_profile, 'resume_text') else 'Not specified'}

            Answer with 'YES:' only if gayle would recommend the candidate for the role.
            Answer with 'NO:' if the candidate is missing important qualifications or experience that would typically disqualify them.

            After your YES/NO, provide 2-3 specific reasons based (quoting) on specific job posting/qualifications mismatches for your decision.
            If NO, include 1-2 specific suggestions for how the candidate could modify their resume or gain experience to become competitive for similar roles in the future.

            ANSWER MUST BEGIN WITH "YES:" OR "NO:"
            """


            # Send the request to Ollama API
            response = requests.post('http://localhost:11434/api/generate',
                                    json={
                                        'model': model_name,
                                        'prompt': prompt,
                                        'temperature': 0.1,
                                        'max_tokens': 512,
                                        'stream': False  # Set to False to get a single response
                                    })

            print(f"DEBUG: RESPONSE: {response.status_code} {response.json()['response']}")
            # Parse the response
            if response.status_code == 200:
                response_data = response.json()
                response_text = response_data['response'].strip().upper()
            else:
                logger.error({"event": "job_selector.llm_is_suitable.response_errored", "job_id": job["id"], "response": response.text, "status_code": response.status_code})
                return False

            is_suitable = "YES" in response_text[:10]  # Check beginning of response for YES
            not_is_suitable = "NO" in response_text[:10]
            rest_of_response = ""
            if is_suitable and not not_is_suitable:
                rest_of_response = response_text.split("YES:")[1]
            elif not_is_suitable and not is_suitable:
                rest_of_response = response_text.split("NO:")[1]
            else:
                logger.error({"event": "job_selector.llm_is_suitable.failed_to_decide", "job_id": job["id"], "response": response_text})
                return False
            job_update = {
                "is_match": is_suitable,
                "match_reason": rest_of_response
            }
            self.storage.update_job(job["id"], job_update)


            return is_suitable


        except Exception as e:
            print(f"Error using Ollama for job suitability evaluation: {str(e)}")
            # Fallback behavior
            return False

    def llm_create_cvs(self, job, user_profile):
        pass


if __name__ == "__main__":
    # TESTING

    ## THE FOLLOWING ARE NOT TRUE SOURCE CODE DEPENDENCIES.
    from src.storage.JobStorage import JobStorage
    from src.profile.Malcolm2025Profile import Malcolm2025Profile

    job_selector = JobSelector(JobStorage())
    profile = Malcolm2025Profile().create_profile()
    job_selector.select_suitable_jobs(profile)
