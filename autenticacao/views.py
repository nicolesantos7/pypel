from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from cadastros.models import Usuario
from django.contrib import messages
from django.http import JsonResponse
from autenticacao import urls
from django.core.mail import EmailMessage

def login(request):
    if request.method == 'POST':
        email = request.POST.get('txtEmail')
        senha = request.POST.get('txtSenha')
        perfil_id = request.POST.get('slcPerfil')

        usuario = authenticate(request, username=email, password=senha)

        if(usuario is not None and perfil_id):
            perfis_usuario = usuario.perfis.filter(id=perfil_id)
            if perfis_usuario.exists():
                request.session.flush()
                auth_login(request, usuario)

                request.session['id_atual'] = usuario.id
                request.session['email_atual'] = usuario.email
                request.session['departamento_id_atual'] = usuario.departamento.id
                request.session['departamento_nome_atual'] = usuario.departamento.nome
                request.session['departamento_sigla_atual'] = usuario.departamento.sigla
                request.session['perfil_atual'] = perfis_usuario.first().nome
                request.session['perfis'] = list(usuario.perfis.values_list('nome', flat=True))
                
                request.session.set_expiry(14400)

                messages.success(request, 'Login realizado com sucesso!')
                
                if request.session.get('perfil_atual') in {'Administrador', 'Estoquista', 'Vendedor'}:
                    return redirect('core:main')
            else:
                messages.error(request, 'Perfil Inválido')
        else:
            if usuario is None:
                messages.error(request, 'Senha errada!')
            else:
                messages.error(request, 'Usuario ou senha invalido!')
    
    return render(request, 'login.html')

def get_perfis(request):
    email = request.GET.get('email', '')
    perfis = []

    if Usuario.objects.filter(email=email).exists():
        usuario = Usuario.objects.get(email=email)
        perfis = usuario.perfis.all().values('id', 'nome')
        data = {'perfis': list(perfis), 'usuario_existe': True}
    else:
        data = {'usuario_existe': False}

    return JsonResponse(data)

def logout(request):
    request.session.flush()
    auth_logout(request)
    messages.success(request, 'Logout realizado com sucesso!')
    
    return redirect('autenticacao:login')

def novaSenha(request):
    if request.method == 'POST':
        try:
            emaildestino = request.POST.get('txtEmail')
            novaSenha = request.POST.get('txtSenha')
            request.session.flush()
            email = EmailMessage(
            'Nova Senha Pypel',
            'Sua nova senha é: ' + novaSenha,
            'privada.games123@gmail.com',
            [emaildestino]
            )
            #email.attach_file('/caminho/para/seu/arquivo.pdf')  # Anexe um arquivo
            email.send()
            messages.success(request, 'Email Enviado com Sucesso!')
            usuario = Usuario.objects.get(email=emaildestino)
            usuario.set_password(novaSenha)
            usuario.save()
            messages.success(request, 'Senha Alterada com Sucesso!')
            return render(request, 'login.html')
        except:
            messages.error(request, 'ERRO 9002 - Deu ruim!')
    return render(request, 'novaSenha.html')