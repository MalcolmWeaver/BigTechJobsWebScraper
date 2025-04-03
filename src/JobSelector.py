from src.storage.JobStorageInterface import JobStorageInterface
import requests

class JobSelector:
    def __init__(self, storage: JobStorageInterface):
        self.storage = storage

    def select_suitable_jobs(self, user_profile):
        jobs = self.storage.get_jobs(filters={"description": True})
        suitable_jobs = []
        for job in jobs[:2]:
            print(f"DEBUG: {job}")
            llm_is_suitable = self.llm_is_suitable(job, user_profile)
            if llm_is_suitable:
                job["is_match"] = True
                # llm_created_cvs = self.llm_create_cvs(job, user_profile)
                # job.generated_cv = llm_created_cvs

            else:
                job["is_match"] = False
        self.storage.update_job(job["id"], job)
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
            You are a strict, experienced recruiter tasked with quickly evaluating job applicants.
            You have many applications to review and need to be selective, especially regarding
            required experience, skills, and qualifications.

            JOB DESCRIPTION:
            {job["title"]}
            {job["description"]}

            Required Skills: {', '.join(job["required_skills"] if hasattr(job, 'required_skills') else [])}
            Required Experience: {job["years_experience"] if hasattr(job, 'years_experience') else 'Not specified'} years

            APPLICANT PROFILE:
            Education: {user_profile.degree if hasattr(user_profile, 'degree') else 'Not specified'}
            Years of Experience: {user_profile.years_of_experience if hasattr(user_profile, 'years_of_experience') else 'Not specified'} years

            Resume: {user_profile.resume_text if hasattr(user_profile, 'resume_text') else 'Not specified'}

            Based solely on the above information, is this applicant suitable for this job?
            Answer only 'YES:' or 'NO:' and then provide a brief explanation for your decision.
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

            print(f"DEBUG: RESPONSE: {response.json()}")
            # Parse the response
            if response.status_code == 200:
                response_data = response.json()
                response_text = response_data['response'].strip().upper()
                is_suitable = "YES" in response_text[:10]  # Check beginning of response for YES

                print(f"DEBUG:Ollama evaluation for job {job['id']}: {'Suitable' if is_suitable else 'Not suitable'}")
                return is_suitable
            else:
                print(f"DEBUG: Ollama API error: {response.status_code} - {response.text}")
                return False

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
    print(f"DEBUG: {vars(profile)}")
    job_selector.select_suitable_jobs(profile)
