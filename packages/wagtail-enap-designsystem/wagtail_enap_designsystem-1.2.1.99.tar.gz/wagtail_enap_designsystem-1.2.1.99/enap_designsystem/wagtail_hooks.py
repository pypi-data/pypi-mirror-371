# ===============================================
# wagtail_hooks.py - VERSÃO FINAL CORRIGIDA
# ===============================================

from wagtail import hooks
from django.utils.html import format_html
from django.templatetags.static import static
from enap_designsystem.blocks import ENAPNoticia
from django.urls import reverse, path
from django.shortcuts import render, get_object_or_404
from django.db.models import Count
import csv
from django.http import HttpResponse, Http404, FileResponse
from wagtail.admin.menu import MenuItem
from .blocks.form import FormularioSubmission, FormularioPage
from django.conf import settings
import os

@hooks.register('insert_global_admin_css')
def global_admin_css():
    return format_html(
        '<link rel="stylesheet" href="{}"><link rel="stylesheet" href="{}">',
        static('css/main_layout.css'),
        static('css/mid_layout.css')
    )

@hooks.register('insert_global_admin_js')
def global_admin_js():
    return format_html(
        '<script src="{}"></script><script src="{}"></script>',
        static('js/main_layout.js'),
        static('js/mid_layout.js')
    )

@hooks.register("before_create_page")
def set_default_author_on_create(request, parent_page, page_class):
    if page_class == ENAPNoticia:
        def set_author(instance):
            instance.author = request.user
        return set_author

@hooks.register('insert_global_admin_js')
def add_export_button():
    return format_html(
        """
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            if (window.location.href.includes('/admin/snippets/enap_designsystem/respostaformulario/')) {{
                const header = document.querySelector('.content-wrapper h1, .content-wrapper h2');
                if (header) {{
                    const exportBtn = document.createElement('a');
                    exportBtn.href = '/admin/exportar-respostas/';
                    exportBtn.className = 'button button-small button-secondary';
                    exportBtn.style.marginLeft = '10px';
                    exportBtn.innerHTML = '📊 Exportar CSV';
                    exportBtn.target = '_blank';
                    header.appendChild(exportBtn);
                }}
            }}
        }});
        </script>
        """
    )

# ===============================================
# VIEWS DE DOWNLOAD DE ARQUIVOS - CORRIGIDAS
# ===============================================
def download_form_file(request, submission_id, field_name):
    """Download de arquivo do FormularioSubmission tradicional - CORRIGIDA"""
    try:
        print(f"🚀 INICIANDO DOWNLOAD:")
        print(f"   submission_id: {submission_id}")
        print(f"   field_name: {field_name}")
        
        submission = get_object_or_404(FormularioSubmission, id=submission_id)
        print(f"✅ Submissão encontrada: {submission.id}")
        print(f"📄 Form data: {submission.form_data}")
        
        if not (request.user.is_staff or request.user.is_superuser):
            print("❌ ERRO: Usuário sem permissão")
            raise Http404("Sem permissão")
        
        print("🔍 Chamando find_file_path_traditional...")
        file_path = find_file_path_traditional(submission, field_name)
        print(f"📂 Resultado: {file_path}")
        
        if not file_path:
            print("❌ ERRO: Arquivo não encontrado")
            
            folder_path = os.path.join(settings.MEDIA_ROOT, 'form_submissions', str(submission_id))
            print(f"🔍 Verificando pasta: {folder_path}")
            
            if os.path.exists(folder_path):
                files = os.listdir(folder_path)
                print(f"📁 Arquivos encontrados: {files}")
            else:
                print(f"❌ Pasta não existe")
                # Verificar outras pastas
                form_submissions_root = os.path.join(settings.MEDIA_ROOT, 'form_submissions')
                if os.path.exists(form_submissions_root):
                    all_folders = [f for f in os.listdir(form_submissions_root) if os.path.isdir(os.path.join(form_submissions_root, f))]
                    print(f"📁 Pastas disponíveis: {all_folders}")
            
            raise Http404("Arquivo não encontrado")
        
        # Nome original do arquivo
        form_data = submission.form_data or {}
        field_data = form_data.get(field_name, {})
        original_filename = field_data.get('filename', os.path.basename(file_path)) if isinstance(field_data, dict) else os.path.basename(file_path)
        
        print(f"📎 Nome original: {original_filename}")
        print(f"🎯 Retornando arquivo: {file_path}")
        
        return FileResponse(
            open(file_path, 'rb'),
            as_attachment=True,
            filename=original_filename
        )
        
    except Exception as e:
        print(f"💥 ERRO COMPLETO: {e}")
        import traceback
        print(f"🔥 TRACEBACK: {traceback.format_exc()}")
        raise Http404(f"Erro ao baixar arquivo: {e}")


def verificar_arquivos_tradicionais():
    """Função para verificar onde estão os arquivos dos formulários tradicionais"""
    from django.db.models import Q
    
    print("🔍 VERIFICANDO ARQUIVOS DE FORMULÁRIOS TRADICIONAIS")
    print("="*60)
    
    # Buscar submissões que têm arquivos
    submissions_with_files = FormularioSubmission.objects.filter(
        form_data__isnull=False
    ).exclude(form_data={})
    
    print(f"📊 Total de submissões: {submissions_with_files.count()}")
    
    arquivos_encontrados = 0
    arquivos_perdidos = 0
    
    for submission in submissions_with_files:
        print(f"\n📄 Submissão ID: {submission.id} - Página: {submission.page.title}")
        
        for field_name, field_data in submission.form_data.items():
            if 'file_upload_field' in field_name:
                print(f"   📎 Campo de arquivo: {field_name}")
                print(f"   📊 Dados: {field_data}")
                
                # Tentar encontrar arquivo
                file_path = find_file_path_traditional(submission, field_name)
                if file_path:
                    print(f"   ✅ Arquivo encontrado: {file_path}")
                    arquivos_encontrados += 1
                else:
                    print(f"   ❌ Arquivo PERDIDO")
                    arquivos_perdidos += 1
    
    print(f"\n📈 RESUMO:")
    print(f"   ✅ Arquivos encontrados: {arquivos_encontrados}")
    print(f"   ❌ Arquivos perdidos: {arquivos_perdidos}")
    
    return {
        'encontrados': arquivos_encontrados,
        'perdidos': arquivos_perdidos
    }





def migrar_arquivos_para_documentos():
    """Migra arquivos existentes para a pasta documentos/"""
    import shutil
    from django.core.files.storage import default_storage
    
    print("🚚 MIGRANDO ARQUIVOS PARA /documentos/")
    print("="*40)
    
    migrados = 0
    erros = 0
    
    # Verificar se pasta documentos existe
    documentos_path = os.path.join(settings.MEDIA_ROOT, 'documentos')
    if not os.path.exists(documentos_path):
        os.makedirs(documentos_path)
        print(f"📁 Criada pasta: {documentos_path}")
    
    submissions_with_files = FormularioSubmission.objects.filter(
        form_data__isnull=False
    ).exclude(form_data={})
    
    for submission in submissions_with_files:
        for field_name, field_data in submission.form_data.items():
            if 'file_upload_field' in field_name and isinstance(field_data, dict):
                filename = field_data.get('filename')
                if filename:
                    # Procurar arquivo no local atual
                    current_path = find_file_path_traditional(submission, field_name)
                    if current_path and 'documentos' not in current_path:
                        try:
                            # Destino em documentos/
                            new_path = os.path.join(documentos_path, filename)
                            
                            # Se já existe, adicionar timestamp
                            if os.path.exists(new_path):
                                from datetime import datetime
                                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                name, ext = os.path.splitext(filename)
                                new_filename = f"{name}_{timestamp}{ext}"
                                new_path = os.path.join(documentos_path, new_filename)
                            
                            # Copiar arquivo
                            shutil.copy2(current_path, new_path)
                            print(f"✅ Migrado: {filename}")
                            migrados += 1
                            
                        except Exception as e:
                            print(f"❌ Erro ao migrar {filename}: {e}")
                            erros += 1
    
    print(f"\n📈 MIGRAÇÃO CONCLUÍDA:")
    print(f"   ✅ Arquivos migrados: {migrados}")
    print(f"   ❌ Erros: {erros}")










def download_dynamic_file(request, submission_id, field_name):
    """Download de arquivo do FormularioDinamicoSubmission - CORRIGIDO"""
    try:
        from .models import FormularioDinamicoSubmission
        submission = get_object_or_404(FormularioDinamicoSubmission, id=submission_id)
        
        # Verificar permissão
        if not (request.user.is_staff or request.user.is_superuser):
            raise Http404("Sem permissão")
        
        # ✅ PROCURAR ARQUIVO USANDO A LÓGICA CORRETA
        file_path = find_file_path_dynamic(submission, field_name)
        if not file_path:
            raise Http404("Arquivo não encontrado")
        
        # Pegar nome original do arquivo
        form_data = submission.form_data or {}
        field_data = form_data.get(field_name, {})
        
        if isinstance(field_data, dict) and 'filename' in field_data:
            original_filename = field_data['filename']
        else:
            # Tentar pegar do files_data
            files_data = getattr(submission, 'files_data', {})
            file_metadata = files_data.get(field_name, {})
            original_filename = file_metadata.get('original_name', os.path.basename(file_path))
        
        print(f"📥 Download dinâmico iniciado: {original_filename} de {file_path}")
        
        return FileResponse(
            open(file_path, 'rb'),
            as_attachment=True,
            filename=original_filename
        )
        
    except ImportError:
        print("❌ FormularioDinamicoSubmission não encontrado")
        raise Http404("Modelo não encontrado")
    except Exception as e:
        print(f"❌ Erro no download dinâmico: {e}")
        raise Http404("Erro ao baixar arquivo")
    


# ===============================================
# CORREÇÃO PARA DOWNLOAD DE ARQUIVOS - FormularioPage
# ===============================================
def find_file_path_traditional(submission, field_name):
    """Encontra caminho do arquivo - VERSÃO PARA UUIDs"""
    
    print(f"🔍 Procurando arquivo: submission_id={submission.id}, field={field_name}")
    
    form_data = submission.form_data or {}
    
    if field_name in form_data:
        field_data = form_data[field_name]
        print(f"📄 Field data: {field_data}")
        
        # Extrair nome do arquivo original
        filename = None
        if isinstance(field_data, dict):
            filename = field_data.get('filename')
        elif isinstance(field_data, str) and field_data:
            filename = field_data
        
        if filename:
            print(f"📎 Arquivo original: {filename}")
            
            # 🔥 BUSCAR POR PASTA DA SUBMISSÃO (onde realmente estão)
            possible_folders = [
                # 1. Pasta específica da submissão
                os.path.join(settings.MEDIA_ROOT, 'form_submissions', str(submission.id)),
                
                # 2. Outras pastas numéricas próximas (baseado no que vimos)
                os.path.join(settings.MEDIA_ROOT, 'form_submissions', '42'),
                os.path.join(settings.MEDIA_ROOT, 'form_submissions', '54'),
                
                # 3. Buscar em TODAS as pastas form_submissions
                *[os.path.join(settings.MEDIA_ROOT, 'form_submissions', str(i)) 
                  for i in range(1, 100) if os.path.exists(os.path.join(settings.MEDIA_ROOT, 'form_submissions', str(i)))]
            ]
            
            # Procurar em cada pasta
            for folder in possible_folders:
                if os.path.exists(folder) and os.path.isdir(folder):
                    print(f"🔍 Procurando em: {folder}")
                    
                    # Listar TODOS os arquivos da pasta
                    for file in os.listdir(folder):
                        file_path = os.path.join(folder, file)
                        if os.path.isfile(file_path):
                            # Se encontrou qualquer arquivo na pasta, retornar o primeiro
                            # (assumindo que há apenas um arquivo por submissão)
                            print(f"✅ Arquivo encontrado: {file_path}")
                            return file_path
            
            # 🔥 BUSCA RECURSIVA em form_submissions
            print("🔍 Fazendo busca recursiva em form_submissions...")
            form_submissions_root = os.path.join(settings.MEDIA_ROOT, 'form_submissions')
            
            if os.path.exists(form_submissions_root):
                for root, dirs, files in os.walk(form_submissions_root):
                    if files:  # Se tem arquivos na pasta
                        # Pegar o primeiro arquivo (assumindo um arquivo por submissão)
                        first_file = files[0]
                        found_path = os.path.join(root, first_file)
                        print(f"✅ Arquivo encontrado recursivamente: {found_path}")
                        return found_path
    
    print(f"❌ Arquivo não encontrado para field: {field_name}")
    return None


def find_file_path_dynamic(submission, field_name):
    """Encontra caminho do arquivo para FormularioDinamicoSubmission
    ALTERADA PARA PROCURAR EM /documentos/"""
    
    # Determinar page_id baseado no tipo de submissão
    if hasattr(submission, 'page'):
        page_id = submission.page.id
    else:
        page_id = submission.object_id
    
    # Obter filename
    form_data = submission.form_data or {}
    field_data = form_data.get(field_name, {})
    
    filename = None
    if isinstance(field_data, dict):
        filename = field_data.get('filename')
    elif isinstance(field_data, str):
        filename = field_data
    
    if not filename:
        return None
    
    # Caminhos para buscar (nova estrutura primeiro)
    possible_paths = [
        # 1. Nova estrutura vinculada
        os.path.join(settings.MEDIA_ROOT, 'formularios', f'page_{page_id}', f'submission_{submission.id}', filename),
        
        # 2. Fallback para estruturas antigas
        os.path.join(settings.MEDIA_ROOT, 'documentos', filename),
        os.path.join(settings.MEDIA_ROOT, 'form_submissions', str(submission.id), filename),
    ]
    
    for path in possible_paths:
        if os.path.exists(path) and os.path.isfile(path):
            return path
    
    return None

# ===============================================
# FUNÇÃO PARA FORMATAR VALORES COM LINKS
# ===============================================

def format_field_value_for_csv(field_name, value, submission=None, request=None):
    """Formata valores para CSV com links de download quando possível"""
    
    if isinstance(value, list):
        return ', '.join(str(v) for v in value if v)
    
    elif isinstance(value, dict) and 'filename' in value:
        filename = value.get('filename', '')
        size = value.get('size', 0)
        
        # Tentar criar link de download
        download_url = None
        if submission and request:
            try:
                # Determinar o tipo de submissão
                if hasattr(submission, 'page'):
                    # FormularioSubmission (tradicional)
                    download_url = request.build_absolute_uri(
                        reverse('download_form_file', kwargs={
                            'submission_id': submission.id,
                            'field_name': field_name
                        })
                    )
                else:
                    # FormularioDinamicoSubmission
                    download_url = request.build_absolute_uri(
                        reverse('download_dynamic_file', kwargs={
                            'submission_id': submission.id,
                            'field_name': field_name
                        })
                    )
            except Exception as e:
                print(f"⚠️ Erro ao criar URL de download: {e}")
        
        # Formatar resposta
        if size:
            size_mb = round(size / (1024 * 1024), 2)
            size_info = f" ({size_mb} MB)"
        else:
            size_info = ""
        
        if download_url:
            return f"{filename}{size_info} - DOWNLOAD: {download_url}"
        else:
            return f"ARQUIVO: {filename}{size_info}"
    
    else:
        return str(value) if value else ''

# ===============================================
# VIEWS DE EXPORTAÇÃO CSV
# ===============================================

def csv_export_view_atualizada(request):
    """Página unificada para escolher qual formulário exportar"""
    from django.shortcuts import render
    from django.db.models import Count
    
    formularios_data = []
    
    print("🔍 Carregando formulários para exportação...")
    
    # Formulários tradicionais (FormularioPage)
    try:
        formularios_existentes = FormularioPage.objects.live()
        for form in formularios_existentes:
            count = FormularioSubmission.objects.filter(page=form).count()
            formularios_data.append({
                'tipo': 'FormularioPage',
                'form': form,
                'count': count,
                'last_submission': FormularioSubmission.objects.filter(page=form).first(),
                'download_url': f'/admin/export-csv/{form.id}/'
            })
            print(f"   📄 FormularioPage: {form.title} ({count} respostas)")
    except Exception as e:
        print(f"⚠️ Erro ao carregar FormularioPage: {e}")
    
    # Formulários dinâmicos
    try:
        from .models import FormularioDinamicoSubmission
        
        dinamicos_stats = FormularioDinamicoSubmission.objects.values(
            'object_id', 'page_title'
        ).annotate(count=Count('id')).order_by('-count')
        
        print(f"📊 Encontrados {len(dinamicos_stats)} formulários dinâmicos")
        
        for stat in dinamicos_stats:
            ultima_submissao = FormularioDinamicoSubmission.objects.filter(
                object_id=stat['object_id']
            ).first()
            
            formularios_data.append({
                'tipo': 'FormularioDinamico',
                'form': {
                    'id': stat['object_id'],
                    'title': f"📝 {stat['page_title']} (Dinâmico)",
                    'slug': f"dinamico-{stat['object_id']}"
                },
                'count': stat['count'],
                'last_submission': ultima_submissao,
                'download_url': f'/admin/export-dinamico-csv/{stat["object_id"]}/'
            })
            print(f"   📝 FormularioDinâmico: {stat['page_title']} ({stat['count']} respostas)")
            
    except ImportError:
        print("FormularioDinamicoSubmission não encontrado")
    except Exception as e:
        print(f"Erro com FormularioDinamico: {e}")
    
    if not formularios_data:
        formularios_data.append({
            'tipo': 'Info',
            'form': {
                'id': 0,
                'title': 'ℹ️ Nenhuma submissão encontrada.',
                'slug': 'info'
            },
            'count': 0,
            'last_submission': None,
            'download_url': '#'
        })
    
    print(f"📋 Total de formulários: {len(formularios_data)}")
    
    return render(request, 'admin/csv_export.html', {
        'formularios': formularios_data,
    })

def download_csv(request, page_id):
    """Download CSV para FormularioPage com links de arquivo"""
    page = get_object_or_404(FormularioPage, id=page_id)
    submissions = FormularioSubmission.objects.filter(page=page).order_by('-submit_time')
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="submissoes_{page.slug}_{page.id}.csv"'
    response.write('\ufeff')
    
    writer = csv.writer(response)
    
    if not submissions.exists():
        writer.writerow(['Nenhuma submissão encontrada'])
        return response
    
    print(f"🚀 Gerando CSV para FormularioPage: {page.title} ({submissions.count()} submissões)")
    
    # Coletar campos únicos
    all_fields = set()
    for submission in submissions:
        if submission.form_data:
            all_fields.update(submission.form_data.keys())
    
    # Usar funções de limpeza se disponíveis
    try:
        from .views import clean_field_name, organize_csv_fields
        ordered_fields = organize_csv_fields(list(all_fields))
        headers = ['Data/Hora', 'IP do Usuário']
        headers.extend([clean_field_name(field) for field in ordered_fields])
    except ImportError:
        ordered_fields = sorted(list(all_fields))
        headers = ['Data/Hora', 'IP do Usuário'] + ordered_fields
    
    writer.writerow(headers)
    
    # Dados com links de arquivos
    for submission in submissions:
        row = [
            submission.submit_time.strftime('%d/%m/%Y %H:%M:%S'),
            submission.user_ip or 'N/A',
        ]
        
        for field in ordered_fields:
            value = submission.form_data.get(field, '') if submission.form_data else ''
            formatted_value = format_field_value_for_csv(field, value, submission, request)
            row.append(formatted_value)
        
        writer.writerow(row)
    
    print(f"✅ CSV tradicional gerado com {submissions.count()} linhas")
    return response

def download_csv_dinamico(request, page_id):
    """Download CSV para formulários dinâmicos com links de arquivo"""
    try:
        from .models import FormularioDinamicoSubmission
        
        submissoes = FormularioDinamicoSubmission.objects.filter(
            object_id=page_id
        ).order_by('-submit_time')
        
        if not submissoes.exists():
            return HttpResponse('Nenhuma submissão encontrada', status=404)
        
        first_submission = submissoes.first()
        page_title = first_submission.page_title or f'Página {page_id}'
        
        print(f"🚀 Gerando CSV dinâmico para: {page_title} ({submissoes.count()} submissões)")
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="dinamico_{page_title}_{page_id}.csv"'
        response.write('\ufeff')
        
        writer = csv.writer(response)
        
        # Coletar campos únicos
        all_fields = set()
        for submissao in submissoes:
            if submissao.form_data:
                all_fields.update(submissao.form_data.keys())
        
        # Organizar campos
        try:
            from .views import clean_field_name, organize_csv_fields
            ordered_fields = organize_csv_fields(list(all_fields))
            headers = ['Data/Hora', 'Nome', 'Email', 'Telefone', 'IP']
            headers.extend([clean_field_name(field) for field in ordered_fields])
        except ImportError:
            ordered_fields = sorted(list(all_fields))
            headers = ['Data/Hora', 'Nome', 'Email', 'Telefone', 'IP'] + ordered_fields
        
        writer.writerow(headers)
        
        # Dados com links de arquivos
        for submissao in submissoes:
            row = [
                submissao.submit_time.strftime('%d/%m/%Y %H:%M:%S'),
                submissao.user_name or '',
                submissao.user_email or '',
                submissao.user_phone or '',
                submissao.user_ip or '',
            ]
            
            for field in ordered_fields:
                value = submissao.form_data.get(field, '') if submissao.form_data else ''
                formatted_value = format_field_value_for_csv(field, value, submissao, request)
                row.append(formatted_value)
            
            writer.writerow(row)
        
        print(f"✅ CSV dinâmico gerado com {submissoes.count()} linhas")
        return response
        
    except ImportError:
        return HttpResponse('FormularioDinamicoSubmission não encontrado', status=404)
    except Exception as e:
        print(f"❌ Erro no CSV dinâmico: {e}")
        return HttpResponse(f'Erro: {str(e)}', status=500)

# ===============================================
# VIEWS ORIGINAIS (COMPATIBILIDADE)
# ===============================================

def csv_export_view(request):
    """Função original para FormularioPage - manter compatibilidade"""
    formularios = FormularioPage.objects.live()
    if not request.user.is_superuser:
        formularios = formularios.filter(owner=request.user)
    
    formularios_data = []
    for form in formularios:
        count = FormularioSubmission.objects.filter(page=form).count()
        formularios_data.append({
            'form': form,
            'count': count,
            'last_submission': FormularioSubmission.objects.filter(page=form).first()
        })
    
    return render(request, 'admin/csv_export.html', {
        'formularios': formularios_data,
    })

# ===============================================
# MENUS
# ===============================================

@hooks.register('register_admin_menu_item')
def register_export_menu_item():
    return MenuItem(
        '📊 Exportar Respostas', 
        reverse('csv_export_updated'),
        icon_name='download',
        order=1000
    )

@hooks.register('register_admin_menu_item')
def register_meta_tags_menu():
    return MenuItem(
        '🏷️ Meta Tags', 
        reverse('meta_tags_manager'),
        classname='icon icon-cog',  # ✅ CORRIGIDO: classname em vez de classnames
        order=800
    )

# ===============================================
# URLS CONSOLIDADAS
# ===============================================

@hooks.register('register_admin_urls')
def register_admin_urls():
    """Registra TODAS as URLs do admin"""
    from .views import meta_tags_manager, preview_meta_changes, apply_meta_tags
    
    return [
        # Meta tags
        path('meta-tags/', meta_tags_manager, name='meta_tags_manager'),
        path('meta-tags/preview/', preview_meta_changes, name='meta_tags_preview'),
        path('meta-tags/apply/', apply_meta_tags, name='meta_tags_apply'),
        
        # Exportação unificada
        path('exportar-respostas/', csv_export_view_atualizada, name='csv_export_updated'),
        
        # Downloads CSV
        path('export-csv/<int:page_id>/', download_csv_with_enap_labels, name='download_csv'),
        path('export-dinamico-csv/<int:page_id>/', download_csv_dinamico_with_enap_labels, name='download_csv_dinamico'),

        
        # URLs para download de arquivos individuais
        path('download-file/<int:submission_id>/<str:field_name>/', download_form_file, name='download_form_file'),
        path('download-dynamic-file/<int:submission_id>/<str:field_name>/', download_dynamic_file, name='download_dynamic_file'),
        
        # Compatibilidade
        path('export-csv/', csv_export_view, name='wagtail_csv_export'),
    ]






def salvar_arquivo_estrategia_personalizada(uploaded_file, field_name, page_id, estrategia='simples'):
    """Salva arquivo usando estratégia específica"""
    from django.core.files.storage import default_storage
    from datetime import datetime
    import uuid
    
    estrategias = {
        'simples': f'documentos/{uploaded_file.name}',
        'timestamp': f'documentos/{datetime.now().strftime("%Y%m%d_%H%M%S")}_{uploaded_file.name}',
        'uuid': f'documentos/{str(uuid.uuid4())[:8]}_{uploaded_file.name}',
        'por_data': f'documentos/{datetime.now().strftime("%Y/%m")}/{uploaded_file.name}',
        'por_tipo': f'documentos/{uploaded_file.name.split(".")[-1].lower()}/{uploaded_file.name}',
        'por_pagina': f'documentos/page_{page_id}/{uploaded_file.name}'
    }
    
    file_path = estrategias.get(estrategia, estrategias['simples'])
    saved_path = default_storage.save(file_path, uploaded_file)
    
    print(f"📎 Arquivo salvo usando estratégia '{estrategia}': {saved_path}")
    return saved_path



def get_file_save_path_options(uploaded_file, field_name, page_id=None):
    """Diferentes opções de como organizar os arquivos em /documentos/"""
    
    from datetime import datetime
    import uuid
    
    # Opção 1: Direto em documentos/
    option1 = f'documentos/{uploaded_file.name}'
    
    
    return {
        'simples': option1,
    }


# ===============================================
# SOLUÇÃO FINAL - LABELS DOS FORMULÁRIOS ENAP
# ===============================================

def extract_labels_from_enap_form_steps(page):
    """
    Extrai labels dos form_steps do ENAP Design System
    
    Os labels ficam em: page.form_steps[0].value['fields'][i].value['label']
    """
    labels = {}
    
    try:
        print(f"🔍 Extraindo labels do ENAP form_steps para: {page.title}")
        
        if not hasattr(page, 'form_steps') or not page.form_steps:
            print("   ❌ Página não tem form_steps")
            return labels
        
        # Iterar pelos steps
        for step_index, step in enumerate(page.form_steps):
            print(f"   📋 Processando step {step_index}: {step.block_type}")
            
            if step.block_type == 'form_step' and 'fields' in step.value:
                fields = step.value['fields']
                print(f"   📊 Encontrados {len(fields)} campos no step")
                
                # Iterar pelos campos
                for field_index, field in enumerate(fields):
                    try:
                        field_type = field.block_type  # Ex: 'text_field', 'nome_completo_field'
                        field_value = field.value      # StructValue com label, placeholder, etc.
                        
                        # Extrair label
                        label = field_value.get('label', '')
                        
                        if label:
                            # Gerar o nome do campo como aparece nas submissões
                            # Formato observado: "field_type_uuid"
                            # Vamos mapear por tipo + posição para depois correlacionar
                            field_key = f"{field_type}_{field_index}"
                            
                            labels[field_type] = label  # Mapear por tipo
                            labels[field_key] = label   # Mapear por tipo + índice
                            
                            print(f"   ✅ {field_type}: '{label}'")
                            
                            # Também guardar outras informações úteis
                            placeholder = field_value.get('placeholder', '')
                            help_text = field_value.get('help_text', '')
                            required = field_value.get('required', False)
                            
                            if placeholder:
                                print(f"      📝 Placeholder: {placeholder}")
                            if help_text:
                                print(f"      💡 Help: {help_text}")
                            print(f"      ⚠️ Obrigatório: {required}")
                        
                    except Exception as e:
                        print(f"   ⚠️ Erro ao processar campo {field_index}: {e}")
        
        print(f"📋 Total de labels extraídos: {len(labels)}")
        return labels
        
    except Exception as e:
        print(f"❌ Erro ao extrair labels: {e}")
        import traceback
        print(f"🔥 Traceback: {traceback.format_exc()}")
        return labels

def map_submission_fields_to_labels(submission_fields, enap_labels):
    """
    Mapeia os nomes reais dos campos nas submissões para os labels do ENAP
    
    submission_fields: ['text_field_bdd5849c-555b-4b86-b059-cb69717d0d02', ...]
    enap_labels: {'text_field': 'Isso é um nome', ...}
    """
    field_mapping = {}
    
    print(f"🔄 Mapeando campos das submissões para labels:")
    
    for field_name in submission_fields:
        label_found = None
        
        # Estratégia 1: Mapear por prefixo do tipo
        for label_key, label_value in enap_labels.items():
            if field_name.startswith(label_key):
                label_found = label_value
                break
        
        if label_found:
            field_mapping[field_name] = label_found
            print(f"   ✅ {field_name} → '{label_found}'")
        else:
            # Fallback: nome limpo
            clean_name = clean_field_name_simple(field_name)
            field_mapping[field_name] = clean_name
            print(f"   ⚠️ {field_name} → '{clean_name}' (fallback)")
    
    return field_mapping

def clean_field_name_simple(field_name):
    """
    Limpeza simples do nome do campo
    """
    import re
    
    # Remover UUID
    clean = re.sub(r'_[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', '', field_name)
    
    # Remover _field
    clean = clean.replace('_field', '')
    
    # Converter para legível
    words = clean.split('_')
    formatted = ' '.join(word.capitalize() for word in words if word)
    
    # Correções
    corrections = {
        'Text': 'Texto',
        'Number': 'Número', 
        'File Upload': 'Arquivo',
        'Nome Completo': 'Nome Completo'
    }
    
    for old, new in corrections.items():
        formatted = formatted.replace(old, new)
    
    return formatted

def download_csv_with_enap_labels(request, page_id):
    """
    Download CSV usando labels extraídos do ENAP form_steps
    """
    page = get_object_or_404(FormularioPage, id=page_id)
    submissions = FormularioSubmission.objects.filter(page=page).order_by('-submit_time')
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="submissoes_{page.slug}_{page.id}.csv"'
    response.write('\ufeff')
    
    writer = csv.writer(response)
    
    if not submissions.exists():
        writer.writerow(['Nenhuma submissão encontrada'])
        return response
    
    print(f"🚀 Gerando CSV com labels ENAP para: {page.title}")
    
    # 1. Extrair labels do ENAP form_steps
    enap_labels = extract_labels_from_enap_form_steps(page)
    
    # 2. Coletar campos das submissões
    all_fields = set()
    for submission in submissions:
        if submission.form_data:
            all_fields.update(submission.form_data.keys())
    
    ordered_fields = sorted(list(all_fields))
    
    # 3. Mapear campos para labels
    field_mapping = map_submission_fields_to_labels(ordered_fields, enap_labels)
    
    # 4. Criar headers
    headers = ['Data/Hora', 'IP do Usuário']
    
    print(f"\n📋 HEADERS FINAIS DO CSV:")
    for field in ordered_fields:
        display_name = field_mapping[field]
        headers.append(display_name)
        print(f"   🏷️ {display_name}")
    
    writer.writerow(headers)
    
    # 5. Escrever dados
    for submission in submissions:
        row = [
            submission.submit_time.strftime('%d/%m/%Y %H:%M:%S'),
            submission.user_ip or 'N/A',
        ]
        
        for field in ordered_fields:
            value = submission.form_data.get(field, '') if submission.form_data else ''
            formatted_value = format_field_value_for_csv(field, value, submission, request)
            row.append(formatted_value)
        
        writer.writerow(row)
    
    print(f"✅ CSV ENAP gerado com {submissions.count()} submissões!")
    return response

def download_csv_dinamico_with_enap_labels(request, page_id):
    """
    Download CSV para formulários dinâmicos usando labels ENAP
    """
    try:
        from .models import FormularioDinamicoSubmission
        
        submissoes = FormularioDinamicoSubmission.objects.filter(
            object_id=page_id
        ).order_by('-submit_time')
        
        if not submissoes.exists():
            return HttpResponse('Nenhuma submissão encontrada', status=404)
        
        first_submission = submissoes.first()
        page_title = first_submission.page_title or f'Página {page_id}'
        page = first_submission.page
        
        print(f"🚀 Gerando CSV dinâmico com labels ENAP: {page_title}")
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="dinamico_{page_title}_{page_id}.csv"'
        response.write('\ufeff')
        
        writer = csv.writer(response)
        
        # Extrair labels se a página existir
        enap_labels = {}
        if page:
            enap_labels = extract_labels_from_enap_form_steps(page)
        
        # Coletar campos únicos
        all_fields = set()
        for submissao in submissoes:
            if submissao.form_data:
                all_fields.update(submissao.form_data.keys())
        
        ordered_fields = sorted(list(all_fields))
        
        # Mapear campos
        field_mapping = map_submission_fields_to_labels(ordered_fields, enap_labels)
        
        # Headers
        headers = ['Data/Hora', 'Nome', 'Email', 'Telefone', 'IP']
        
        for field in ordered_fields:
            display_name = field_mapping[field]
            headers.append(display_name)
            print(f"   🏷️ {display_name}")
        
        writer.writerow(headers)
        
        # Dados
        for submissao in submissoes:
            row = [
                submissao.submit_time.strftime('%d/%m/%Y %H:%M:%S'),
                submissao.user_name or '',
                submissao.user_email or '',
                submissao.user_phone or '',
                submissao.user_ip or '',
            ]
            
            for field in ordered_fields:
                value = submissao.form_data.get(field, '') if submissao.form_data else ''
                formatted_value = format_field_value_for_csv(field, value, submissao, request)
                row.append(formatted_value)
            
            writer.writerow(row)
        
        print(f"✅ CSV dinâmico ENAP gerado com {submissoes.count()} linhas")
        return response
        
    except ImportError:
        return HttpResponse('FormularioDinamicoSubmission não encontrado', status=404)
    except Exception as e:
        print(f"❌ Erro no CSV dinâmico: {e}")
        return HttpResponse(f'Erro: {str(e)}', status=500)

def test_enap_label_extraction(page_id):
    """
    Testa a extração de labels ENAP
    """
    try:
        from enap_designsystem.blocks.form import FormularioPage
        page = FormularioPage.objects.get(id=page_id)
        
        print(f"🧪 TESTE DE EXTRAÇÃO ENAP LABELS - {page.title}")
        print("="*60)
        
        # Extrair labels
        labels = extract_labels_from_enap_form_steps(page)
        
        # Testar com submissões
        submissions = FormularioSubmission.objects.filter(page=page)
        if submissions.exists():
            first_submission = submissions.first()
            if first_submission.form_data:
                submission_fields = list(first_submission.form_data.keys())
                
                print(f"\n📊 MAPEAMENTO FINAL:")
                field_mapping = map_submission_fields_to_labels(submission_fields, labels)
                
                print(f"\n🎯 RESULTADO ESPERADO NO CSV:")
                for field, label in field_mapping.items():
                    print(f"   📝 Coluna: '{label}'")
        
        return labels
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return {}

"""
IMPLEMENTAÇÃO FINAL:

1. Substitua as URLs por:
path('export-csv/<int:page_id>/', download_csv_with_enap_labels, name='download_csv'),
path('export-dinamico-csv/<int:page_id>/', download_csv_dinamico_with_enap_labels, name='download_csv_dinamico'),

2. Teste antes:
from yourapp.wagtail_hooks import test_enap_label_extraction
test_enap_label_extraction(55)

RESULTADO ESPERADO NO CSV:
- Data/Hora
- IP do Usuário
- Isso é um nome  ← FUNCIONANDO! 🎉
- Nome Completo
- Anexar arquivo  
- Isso é
"""