from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseNotFound, HttpResponseBadRequest, FileResponse, Http404, JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils.translation import gettext as _, activate
from django.utils import translation
from datetime import datetime
import os
import json
import logging
from django.views.decorators.csrf import csrf_exempt
from .services import centralized_log, DynamicLogger, dynamic_log, log_step, log_info, log_warning, log_error

# Constants
DEFAULT_LOG_LIMIT = 50
MAX_LOG_LIMIT = 1000
SUPPORTED_LOG_LEVELS = ['INFO', 'WARNING', 'ERROR', 'DEBUG', 'CRITICAL']

logger = logging.getLogger(__name__)


def change_language(request):
    """
    Dil değiştirme view'ı
    """
    lang = request.GET.get('lang', 'en')
    if lang in ['tr', 'en']:
        # Set session key according to Django version
        if hasattr(translation, 'LANGUAGE_SESSION_KEY'):
            request.session[translation.LANGUAGE_SESSION_KEY] = lang
        else:
            # For old Django versions
            request.session['django_language'] = lang
        # Activate language change
        translation.activate(lang)
    return redirect('log_hub:log_view')


@csrf_exempt
def test_custom_logging(request):
    """Merkezi loglama sistemini test etmek için view"""
    if request.method == 'POST':
        test_type = request.POST.get('test_type', 'basic')
        
        # Get user information more reliably
        user_id = 'anonymous'
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_id = getattr(request.user, 'username', str(request.user.id))
        elif hasattr(request, 'user') and request.user:
            user_id = getattr(request.user, 'username', str(request.user.id))
        
        if test_type == 'basic':
            # Basic centralized logging test
            with DynamicLogger("Temel Test İşlemi", user_id=user_id) as logger:
                logger.step("Test başladı", {"test_type": "basic"})
                logger.step("Test adımı", {"step": 1})
                logger.step("Test tamamlandı", {"result": "success"})
            
            return JsonResponse({
                'success': True,
                'message': 'Basic centralized logging test completed'
            })
        
        elif test_type == 'centralized':
            # Centralized logging test - all steps saved at once
            with DynamicLogger("Merkezi Test İşlemi", user_id=user_id) as logger:
                logger.step("Veri Hazırlama", {"data_type": "test_data"})
                logger.step("İşlem Yürütme", {"process": "test_process"})
                logger.step("Sonuç Kontrolü", {"check": "validation"})
                logger.warning("Dikkat: Test uyarısı", {"warning_type": "test"})
                
                logger.finish(save_logs=True)
                
            return JsonResponse({
                'success': True,
                'message': 'Centralized logging test completed - all steps saved in one line'
            })
        
        elif test_type == 'dynamic':
            # Dynamic logging test - automatic entry/exit
            with DynamicLogger("Dinamik Test İşlemi", user_id=user_id) as logger:
                logger.step("Veri hazırlanıyor", {"data_type": "test_data"})
                logger.step("İşlem yürütülüyor", {"process": "test_process"})
                logger.step("Sonuç kontrol ediliyor", {"check": "validation"})
                logger.warning("Dikkat: Test uyarısı", {"warning_type": "test"})
                logger.step("Response hazırlanıyor", {"status_code": 200, "content_type": "application/json"})
                
                logger.finish(save_logs=True)
                
            return JsonResponse({
                'success': True,
                'message': 'Dynamic logging test completed - automatic entry/exit logging'
            })
        
        elif test_type == 'endpoint_simulation':
            # Endpoint simulation - like a real API endpoint
            with DynamicLogger("API Endpoint İşlemi", user_id=user_id) as logger:
                logger.step("Request Alındı", {"method": "POST", "endpoint": "/api/test"})
                logger.step("Parametre Doğrulama", {"params": {"id": 123, "name": "test"}})
                logger.step("Veritabanı Sorgusu", {"query": "SELECT * FROM users WHERE id=123"})
                logger.step("İş Mantığı", {"business_logic": "kullanıcı güncelleme"})
                logger.step("Response Hazırlama", {"status_code": 200, "data_size": 1024})
                
                logger.finish(save_logs=True)
                
            return JsonResponse({
                'success': True,
                'message': 'Endpoint simulation completed - all steps saved in one line'
            })
        
        elif test_type == 'error':
            # Error logging test
            with DynamicLogger("Hata Test İşlemi", user_id=user_id) as logger:
                logger.step("İlk Adım", {"step": 1})
                logger.warning("Dikkat: Test uyarısı", {"warning_type": "test"})
                logger.error("Test hatası oluştu", {"error_type": "simulated"})
                
                logger.finish(save_logs=True)
                
            return JsonResponse({
                'success': True,
                'message': 'Error logging test completed'
            })
    
    return render(request, 'log_hub/test_logging.html')


@centralized_log("Example Centralized Operation")
def example_centralized_function(user_id, operation_data):
    """Example function to demonstrate centralized logging decorator usage"""
    # This function will be automatically logged with centralized logging
    # All steps will be saved in one line but displayed line by line in HTML
    
    # Simulated operation steps
    result = {
        "user_id": user_id,
        "processed_data": operation_data,
        "status": "completed"
    }
    return result


@dynamic_log("Example Dynamic Operation")
def example_dynamic_function(user_id, operation_data):
    """Example function to demonstrate dynamic logging decorator usage"""
    # This function will be automatically logged with dynamic logging
    # Entry/exit automatic, only step messages will be written
    
    # Simulated operation steps
    result = {
        "user_id": user_id,
        "processed_data": operation_data,
        "status": "completed"
    }
    return result


@csrf_exempt
def test_decorator_logging(request):
    """Centralized decorator logging test"""
    if request.method == 'POST':
        try:
            # Call function with test data
            result = example_centralized_function("test_user", {"test": "data"})
            
            return JsonResponse({
                'success': True,
                'message': 'Centralized decorator logging test completed',
                'result': result
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Hata: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'POST metodu gerekli'
    })


@csrf_exempt
def test_dynamic_logging(request):
    """Dynamic decorator logging test"""
    if request.method == 'POST':
        try:
            # Call function with test data
            result = example_dynamic_function("test_user", {"test": "data"})
            
            return JsonResponse({
                'success': True,
                'message': 'Dynamic decorator logging test completed',
                'result': result
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Hata: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'POST metodu gerekli'
    })


def parse_log_line(line):
    """
    Log satırını JSON formatından parse eder
    Hem eski format hem de yeni AggregatedLogger formatını destekler
    """
    try:
        log_data = json.loads(line.strip())
        
        # Yeni AggregatedLogger formatı kontrolü
        if "lines" in log_data and "header" in log_data:
            # AggregatedLogger formatı - lines alanından adımları al
            lines = log_data.get("lines", [])
            header = log_data.get("header", "")
            header_context = log_data.get("header_context", {})
            timestamp = log_data.get("timestamp", "")
            level = log_data.get("level", "INFO")
            
            # Tüm adımları birleştir
            all_messages = []
            for line_entry in lines:
                log_message = line_entry.get("message", "")
                log_level = line_entry.get("level", "INFO")
                
                # Add level information
                if log_level != "INFO":
                    log_message = f"[{log_level}] {log_message}"
                
                # Django traceback check - if it's a traceback, keep it as is
                if "Traceback (most recent call last):" in log_message or "File \"" in log_message:
                    # Preserve Django's own format, don't make it line by line
                    # Remove excessive whitespace from traceback lines
                    lines = log_message.split('\n')
                    cleaned_lines = []
                    for line in lines:
                        stripped = line.strip()
                        if stripped:  # Only add non-empty lines
                            cleaned_lines.append(stripped)
                    cleaned_message = '\n'.join(cleaned_lines)
                    all_messages.append(cleaned_message)
                else:
                    # Make user's written messages line by line
                    all_messages.append(log_message.strip())
            
            # Parse timestamp
            try:
                if timestamp:
                    asctime = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                else:
                    asctime = datetime.now()
            except:
                asctime = datetime.now()
            
            # Extract HTTP status code from header_context
            status_code = "200"  # Default success code
            if "status_code" in header_context:
                status_code = str(header_context["status_code"])
            
            # Get user information from header context
            user_info = header_context.get("user", "anonymous")
            
            return {
                "level": level,
                "name": log_data.get("logger_name", "AggregatedLogger"),
                "asctime": asctime,
                "timestamp": timestamp,
                "message": f"{header} | User: {user_info} | Steps: {len(lines)}",  # Summary info
                "status_code": status_code,
                "task_name": header,
                "request": f"Operation: {header} | User: {user_info} | Steps: {len(lines)}",
                "info": all_messages,  # Alt alta görünmesi için
                "raw": line,
            }
        
        # Old centralized logging format check
        elif "header" in log_data and "logs" in log_data:
            # Centralized logging format - combine all steps
            header = log_data["header"]
            logs = log_data["logs"]
            
            # Get information from first log record
            if logs:
                first_log = logs[0]
                timestamp = first_log.get("timestamp", "")
                level = first_log.get("level", "INFO")
                message = first_log.get("message", "")
                
                # Combine all steps
                all_messages = []
                for log_entry in logs:
                    log_message = log_entry.get("message", "")
                    log_context = log_entry.get("context", {})
                    
                    # Add context information
                    if log_context:
                        context_str = " | ".join([f"{k}: {v}" for k, v in log_context.items() if v])
                        if context_str:
                            log_message += f" [{context_str}]"
                    
                    # Django traceback check - if it's a traceback, keep it as is
                    if "Traceback (most recent call last):" in log_message or "File \"" in log_message:
                        # Preserve Django's own format, don't make it line by line
                        # Remove excessive whitespace from traceback lines
                        lines = log_message.split('\n')
                        cleaned_lines = []
                        for line in lines:
                            stripped = line.strip()
                            if stripped:  # Only add non-empty lines
                                cleaned_lines.append(stripped)
                        cleaned_message = '\n'.join(cleaned_lines)
                        all_messages.append(cleaned_message)
                    else:
                        # Make user's written messages line by line
                        all_messages.append(log_message.strip())
                
                # Tarihi parse et
                try:
                    if timestamp:
                        asctime = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    else:
                        asctime = datetime.now()
                except:
                    asctime = datetime.now()
                
                # Try to extract HTTP status code from logs
                status_code = "200"  # Default success code
                for log_entry in logs:
                    log_context = log_entry.get("context", {})
                    if "status_code" in log_context:
                        status_code = str(log_context["status_code"])
                        break
                    elif "step_details" in log_context and "status" in log_context["step_details"]:
                        # Get status code from response preparation step
                        if "status" in log_context["step_details"]:
                            status_code = str(log_context["step_details"]["status"])
                            break
                
                return {
                    "level": level,
                    "name": "CentralizedLogger",
                    "asctime": asctime,
                    "timestamp": timestamp,
                    "message": f"{header.get('operation_id', 'N/A')} | User: {header.get('user_id', 'N/A')} | Logs: {len(logs)}",  # Summary info
                    "status_code": status_code,
                    "task_name": header.get("operation_id", ""),
                    "request": f"Operation: {header.get('operation_id', 'N/A')} | User: {header.get('user_id', 'N/A')} | Logs: {len(logs)}",
                    "info": all_messages,  # For line-by-line display
                    "raw": line,
                }
        
        # Old format - single log record
        level = log_data.get("levelname", "UNKNOWN")
        exc_info = log_data.get("exc_info", "")
        info = exc_info.split("\n") if exc_info else []

        # Convert timestamp to milliseconds
        asctime_str = log_data.get("asctime", "")
        try:
            asctime = datetime.strptime(asctime_str, "%Y-%m-%d %H:%M:%S,%f")
        except:
            try:
                asctime = datetime.fromisoformat(asctime_str.replace('Z', '+00:00'))
            except:
                asctime = datetime.now()

        return {
            "level": level,
            "name": log_data.get("name", ""),
            "asctime": asctime,
            "timestamp": asctime_str,
            "message": log_data.get("message", ""),
            "status_code": log_data.get("status_code", ""),
            "task_name": log_data.get("taskName", ""),
            "request": log_data.get("request", ""),
            "info": info,
            "raw": line,
        }
    except json.JSONDecodeError as e:
        return {
            "level": "ERROR",
            "timestamp": "",
            "message": "Invalid JSON format",
            "status_code": "",
            "task_name": "",
            "request": "",
            "raw": line,
        }


@login_required
@user_passes_test(lambda u: u.is_staff)
def log_view(request):
    """
    View for displaying log files
    """
    try:
        # Get log directory (from settings or default)
        log_dir = getattr(settings, 'LOG_HUB_LOG_DIR', os.path.join(settings.BASE_DIR, 'logs'))
        
        # Check log directory
        if not os.path.exists(log_dir):
            template_name = getattr(settings, 'LOG_HUB_TEMPLATE', 'log_hub/logging.html')
            return render(request, template_name, {
                "hata": _("Log directory not found: %(dir)s") % {"dir": log_dir},
                'log_count': 0,
                'logs': [],
                'log_files': [],
                'selected_log_type': None,
                'search_query': '',
                'log_level': '',
                'start_date': '',
                'end_date': '',
                'limit': DEFAULT_LOG_LIMIT,
                'status_code': '',
                'exclude': '',
                'LANGUAGE_CODE': translation.get_language(),
            })
        
        log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]  # Find .log files
        
        # If no log files
        if not log_files:
            template_name = getattr(settings, 'LOG_HUB_TEMPLATE', 'log_hub/logging.html')
            return render(request, template_name, {
                "hata": _("No .log files found in directory: %(dir)s") % {"dir": log_dir},
                'log_count': 0,
                'logs': [],
                'log_files': [],
                'selected_log_type': None,
                'search_query': '',
                'log_level': '',
                'start_date': '',
                'end_date': '',
                'limit': DEFAULT_LOG_LIMIT,
                'status_code': '',
                'exclude': '',
                'LANGUAGE_CODE': translation.get_language(),
            })
        
        log_type = request.GET.get('log_type', log_files[0] if log_files else None)  # Selected log file
        search_query = request.GET.get('q', '')  # Search term
        log_level = request.GET.get('level', '')  # Log level (INFO, ERROR, WARNING)
        limit = int(request.GET.get('limit', DEFAULT_LOG_LIMIT))  # Number of logs to show
        limit = min(limit, MAX_LOG_LIMIT)  # Maximum limit check
        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')
        status_code = request.GET.get('status_code', '') # status koduna göre listele
        exclude = request.GET.get('exclude', '') # Listelerken hariç tutulacak log satırları(anahtar kelimeler)

        if log_type and log_type in log_files:
            log_file_path = os.path.join(log_dir, log_type)
        else:
            template_name = getattr(settings, 'LOG_HUB_TEMPLATE', 'log_hub/logging.html')
            return render(request, template_name, {
                "hata": _("Selected log file not found: %(file)s") % {"file": log_type},
                'log_count': 0,
                'logs': [],
                'log_files': log_files,
                'selected_log_type': log_files[0] if log_files else None,
                'search_query': search_query,
                'log_level': log_level,
                'start_date': start_date,
                'end_date': end_date,
                'limit': limit,
                'status_code': status_code,
                'exclude': exclude,
                'LANGUAGE_CODE': translation.get_language(),
            })
        
        try:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%dT%H:%M") if start_date else None
            end_datetime = datetime.strptime(end_date, "%Y-%m-%dT%H:%M") if end_date else None
        except ValueError:
            template_name = getattr(settings, 'LOG_HUB_TEMPLATE', 'log_hub/logging.html')
            return render(request, template_name, {
                "hata": _("Invalid date format. Please use 'YYYY-MM-DDTHH:MM' format."),
                'log_count': 0,
                'logs': [],
                'log_files': log_files,
                'selected_log_type': log_type,
                'search_query': search_query,
                'log_level': log_level,
                'start_date': start_date,
                'end_date': end_date,
                'limit': limit,
                'status_code': status_code,
                'exclude': exclude,
                'LANGUAGE_CODE': translation.get_language(),
            })

        logs = []
        hata = None
        try:
            with open(log_file_path, 'r', encoding='utf-8') as file:
                exclude_keywords = [kelime.strip().lower() for kelime in exclude.split(",") if kelime.strip()]
                s = 0
                
                # Dosyayı sondan başlayarak oku (son logları göster)
                lines = file.readlines()
                for line in reversed(lines):  # Sondan başla
                    log_data = parse_log_line(line)
                    
                    # Filtreleme
                    if exclude and any(kelime in line.lower() for kelime in exclude_keywords):
                        continue
                    if status_code and str(status_code) != str(log_data["status_code"]):
                        continue
                    if log_level and log_level != log_data["level"]:
                        continue
                    if search_query and search_query.lower() not in log_data["raw"].lower():
                        continue
                    if start_datetime and log_data["asctime"] and log_data["asctime"] < start_datetime:
                        continue
                    if end_datetime and log_data["asctime"] and log_data["asctime"] > end_datetime:
                        continue
                    
                    logs.append(log_data)
                    s += 1
                    if s >= int(limit):
                        break
        except UnicodeDecodeError as e:
            hata = _("Log file encoding error: %(error)s. File must be in UTF-8 format.") % {"error": str(e)}
        except PermissionError as e:
            hata = _("No permission to access log file: %(error)s") % {"error": str(e)}
        except Exception as e:
            hata = _("Error reading log file: %(error)s") % {"error": str(e)}

        # Template path'ini settings'den al veya varsayılan kullan
        template_name = getattr(settings, 'LOG_HUB_TEMPLATE', 'log_hub/logging.html')

        return render(request, template_name, {
            "hata": hata,
            'log_count': len(logs),
            'logs': logs,
            'log_files': log_files,
            'selected_log_type': log_type,
            'search_query': search_query,
            'log_level': log_level,
            'start_date': start_date,
            'end_date': end_date,
            'limit': limit,
            'status_code': status_code,
            'exclude': exclude,
            'LANGUAGE_CODE': translation.get_language(),
        })
    except Exception as e:
        template_name = getattr(settings, 'LOG_HUB_TEMPLATE', 'log_hub/logging.html')
        return render(request, template_name, {
            "hata": _("An unexpected error occurred: %(error)s") % {"error": str(e)},
            'log_count': 0,
            'logs': [],
            'log_files': [],
            'selected_log_type': None,
            'search_query': '',
            'log_level': '',
            'start_date': '',
            'end_date': '',
            'limit': DEFAULT_LOG_LIMIT,
            'status_code': '',
            'exclude': '',
            'LANGUAGE_CODE': translation.get_language(),
        })


@staff_member_required
@require_http_methods(["POST"])
def clear_log(request, log_file_name):
    """
    Log dosyasını temizlemek için view
    """
    # Güvenlik: Dosya adı doğrulaması
    if not log_file_name or not log_file_name.endswith('.log') or '..' in log_file_name or '/' in log_file_name:
        return JsonResponse({"status": "error", "message": _("Invalid log file name")}, status=400)
    
    log_dir = getattr(settings, 'LOG_HUB_LOG_DIR', os.path.join(settings.BASE_DIR, 'logs'))
    log_file_path = os.path.join(log_dir, log_file_name)
    
    # Güvenlik: Path traversal kontrolü
    if not os.path.abspath(log_file_path).startswith(os.path.abspath(log_dir)):
        return JsonResponse({"status": "error", "message": _("Access denied")}, status=403)

    if not os.path.exists(log_file_path):
        raise Http404(_("Specified log file not found."))
    
    try:
        with open(log_file_path, 'w'):
            pass  # Dosya içeriğini temizle

        return JsonResponse({"status": "success", "message": _("'%(file)s' successfully cleared.") % {"file": log_file_name}})
    except Exception as e:
        return JsonResponse({"status": "error", "message": _("Error clearing file: %(error)s") % {"error": str(e)}}, status=500)


@staff_member_required
def download_log(request, log_file_name):
    """
    Log dosyasını indirmek için view
    """
    # Güvenlik: Dosya adı doğrulaması
    if not log_file_name or not log_file_name.endswith('.log') or '..' in log_file_name or '/' in log_file_name:
        raise Http404(_("Invalid log file name"))
    
    log_dir = getattr(settings, 'LOG_HUB_LOG_DIR', os.path.join(settings.BASE_DIR, 'logs'))
    log_file_path = os.path.join(log_dir, log_file_name)
    
    # Güvenlik: Path traversal kontrolü
    if not os.path.abspath(log_file_path).startswith(os.path.abspath(log_dir)):
        raise Http404(_("Access denied"))

    if not os.path.exists(log_file_path):
        raise Http404(_("Selected log file not found."))

    return FileResponse(open(log_file_path, 'rb'), as_attachment=True, filename=log_file_name)
