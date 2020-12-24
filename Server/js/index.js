
function handleClick(radio_btn)
{
    var radio_btn_value = radio_btn.value;
    var login_form = document.getElementById('login-form');
    var register_form = document.getElementById('register-form');

    if (radio_btn_value === 'login')
    {
        login_form.style.display = '';
        register_form.style.display = 'none';
    }
    else
    {
        login_form.style.display = 'none';
        register_form.style.display = '';
    }
}

function user_cookies()
{
    var cs = document.cookie;;
    var user_name = getCookie('user_name', cs);
    var email = getCookie('email', cs);
    var password = getCookie('user_name', cs);
    var template_block = document.getElementById('template-area');
    var task_block = document.getElementById('task');
    template_block.innerHTML = "";

    console.log(user_name)

    if (user_name !== '' && email !== '' && password !== '')
    {
        task_block.style.display = 'block';
        template_block.innerHTML = '<div id = "logout-area">\n'+
            '<form action="api/logout" method="post">\n'+
            '<input type="submit" value="Вийти" id="logout-button">\n'+
            '</form>\n'+
            '</div>\n';
    }
    else
    {
        task_block.style.display = 'none';
        template_block.innerHTML = '\
            <div id = "login-area">\
                <div style = "display: block;">\
                    <ul id = "change-reg">\
                        <li>\
                            <input class = "input-radio-log-reg" type="radio" value="login" name="radio-log-reg" id="login-radio" onclick="handleClick(this);" checked/>\
                            <label id = "login-radio-label" for="login-radio">Login</label>\
                        </li>\
                        <li>\
                            <input class = "input-radio-log-reg" type="radio" value="register" name="radio-log-reg" id="reg-radio" onclick="handleClick(this);"/>\
                            <label id = "reg-radio-label" for="reg-radio">Register</label>\
                        </li>\
                    </ul>\
                </div>\
                <div>\
                    <form id = "login-form" action="api/login" method="post">\
                        <input type="email" id="login-email" name = "email" placeholder = "Пошта" required>\
                        <input type="password" id="login-password" name = "password" placeholder = "Пароль" required>\
                        <input type="submit" value="Вхід" id="login-button">\
                    </form>\
                    <form id = "register-form" action="api/register" method="post" style = "display: none;">\
                        <input type="text" id="reg-name" name = "user_name" placeholder = "Ім\'я" required>\
                        <input type="email" id="reg-email" name = "email" placeholder = "Пошта" required>\
                        <input type="password" id="reg-password" name = "password" placeholder = "Пароль" required>\
                        <input type="submit" value="Реєстрація" id="register-button">\
                    </form>\
                </div>\
            </div>';
    }

    load_results();
}

function getCookie(cname, cs)
{
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(cs);
    var ca = decodedCookie.split(';');
    for(var i = 0; i < ca.length; i++) {
      var c = ca[i];
      while (c.charAt(0) == ' ') {
        c = c.substring(1);
      }
      if (c.indexOf(name) == 0) {
        return c.substring(name.length, c.length);
      }
    }
    return "";
}

function calculate_task()
{
    var comments_area = document.getElementById("comments-area");
    var comment_ = document.createElement("li");
    var error_message_area = document.getElementById("error-message");
    var list_ = document.getElementById("task-area-input-form");
    var list_items = list_.getElementsByTagName("li");
    
    var list_elements = [];
    var list_element = 0;
    for (var i = 0; i < list_items.length; ++i) {
        list_element = list_items[i].children[0].value;
        var parsed_elem = parseFloat(list_element);

        if (isNaN(parsed_elem) === true && list_element !== "")
        {
            error_message_area.style.display = '';
            window.setTimeout(function(){ error_message_area.style.display = 'none'; }, 3500);

            return false;
        }
        if (list_element !== "")        
        {
            list_elements.push(parsed_elem);
        }
    }

    if (list_elements.length === 0)
    {
        return false;
    }
    
    var xml_req = new XMLHttpRequest();
    xml_req.open("POST", "/api/task", true);
    xml_req.send(JSON.stringify(list_elements));
    
    xml_req.onload = function(e) 
    {
        /*var res = JSON.parse(xml_req.responseText);
        var username = res.user_name;
        var task_data = res.task_data;
        var result = res.result;

        comment_.innerHTML = `<strong>Введені дані:</strong> <i>${task_data}</i>. <strong>Результат:</strong> <i>${result}</i>.  <i><strong>${username}</strong></i>`;
        comment_.setAttribute('class', 'comments-li')
        comments_area.appendChild(comment_);*/
        load_results();
    }
}

function add_node()
{
    var list_ = document.getElementById("task-area-input-form");
    var list_item = document.createElement("li");
    var input_ = document.createElement("input");

    input_.setAttribute("class", "data_input");
    list_item.appendChild(input_);
    list_.appendChild(list_item);
}

function delete_node()
{
    var list_ = document.getElementById("task-area-input-form");
    var list_items = list_.getElementsByTagName("li");

    if (list_items.length == 1)
    {
        return false;
    }
    list_.removeChild(list_.lastElementChild);
}

function load_results()
{
    var comments_area = document.getElementById("comments-area");
    comments_area.innerHTML = "";

    var xml_req = new XMLHttpRequest();
    xml_req.open("GET", "/api/task", true);
    xml_req.send();
    xml_req.onload = function (e)
    {
        var solutions = JSON.parse(xml_req.responseText);
        
        for (var key in solutions) 
        {
            var user = solutions[key];
            var username = user.user_name;
            var task_data = user.task_data;
            var result = user.result;

            var comment_ = document.createElement("li");
            comment_.innerHTML = `<strong>Введені дані:</strong> <i>${task_data}</i>. <strong>Результат:</strong> <i>${result}</i>.  <i><strong>${username}</strong></i>`;
            comment_.setAttribute('class', 'comments-li')
            comments_area.appendChild(comment_);
        }
    }
}

//user_cookies()
