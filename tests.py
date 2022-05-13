import requests as request

host_address = ""

def test():   
    response = request.get("http://54.221.34.219:6969/classroom/signup/teacher_signup/")
    assert 200 == response.status_code

    response = request.get("http://54.221.34.219:6969/classroom/signup/student_signup/")
    assert 200 == response.status_code

    response = request.get("http://54.221.34.219:6969/classroom/students_list/")
    assert 200 != response.status_code

    response = request.get("http://54.221.34.219:6969/classroom/teachers_list/")
    assert 200 == response.status_code



test()