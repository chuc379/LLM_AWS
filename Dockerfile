FROM public.ecr.aws/lambda/python:3.12

# Thư mục làm việc mặc định của Lambda là ${LAMBDA_TASK_ROOT}
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements của LLM_AWS và cài đặt dependency
COPY LLM_AWS/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn LLM_AWS vào image
COPY LLM_AWS/ ./LLM_AWS/

# Entry point cho Lambda: module LLM_AWS.main với biến handler (Mangum)
CMD [ "LLM_AWS.main.handler" ]

