from datetime import datetime, timedelta
from textwrap import dedent

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator

from utils.callbacks import failure_callback, success_callback

local_timezone = pendulum.timezone("Asia/Seoul")

with DAG(
    # DONE: "simple_dag"이라는 이름의 DAG 설정
    dag_id="simple_dag",
    # DONE: default_args에는 다음 내용이 들어감
    # DONE: "user" 사용자가 소유한 DAG / 본인의 이메일 / 실패 및 재시도 시 이메일 알림 여부
    # DONE: 재시도 1회 / 재시도 간격 5분
    # DONE: 실패 시 callback (failure_callback) / 성공 시 callback (success_callback)
    default_args={
        "owner": "user",
        "depends_on_past": False,
        "email": "akino0604@lgcns.com",
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "on_failure_callback": failure_callback,
        "on_success_callback": success_callback,
    },
    description="Simple airflow dag",
    schedule="0 15 * * *",
    start_date=datetime(2025, 3, 1, tzinfo=local_timezone),
    catchup=False, # 안된 게 있으면 한번에 다 돌릴 것
    tags=["lgcns", "mlops"], # 왠만해서 넣으면 조회하기 편함
) as dag:
    task0 = EmptyOperator(task_id="empty")
    task1 = BashOperator(
        task_id="print_date",
        # DONE: 현재 시간을 출력하는 bash_command 입력
        bash_command="date",
    )
    task2 = BashOperator(
        task_id="sleep",
        depends_on_past=False,
        # DONE: 5초 sleep하는 bash_command를 입력하고 3회 재시도하도록 설정
        bash_command="sleep 5",
        retries = 3
    )

    loop_command = dedent(
        """
        {% for i in range(5) %}
            echo "ds = {{ ds }}"
            echo "macros.ds_add(ds, {{ i }}) = {{ macros.ds_add(ds, i) }}"
        {% endfor %}
        """
    )
    task3 = BashOperator(
        task_id="print_with_loop",
        bash_command=loop_command,
    )

    task0 >> task1 >> [task2, task3]
    # task1 >> task2 >> task3
    
