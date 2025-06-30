from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Client, Card, Transaction
from .mindsdb_util import mindsdb_util


def index(request):
    """Main dashboard view"""
    context = {
        'total_clients': Client.objects.count(),
        'total_cards': Card.objects.count(),
        'total_transactions': Transaction.objects.count(),
        'recent_transactions': Transaction.objects.select_related('client', 'card').order_by('-date')[:10],
    }
    return render(request, 'finance/index.html', context)


@csrf_exempt
@require_http_methods(["GET"])
def api_clients(request):
    """API endpoint to get all clients"""
    clients = Client.objects.all()[:25]
    data = []
    for client in clients:
        data.append({
            'id': client.id,
            'current_age': client.current_age,
            'retirement_age': client.retirement_age,
            'gender': client.gender,
            'per_capita_income': float(client.per_capita_income),
            'address': client.address,
            'latitude': float(client.latitude),
            'longitude': float(client.longitude),
        })
    return JsonResponse({'clients': data})


@csrf_exempt
@require_http_methods(["GET"])
def api_cards(request):
    """API endpoint to get all cards"""
    cards = Card.objects.select_related('client').all()[:25]
    data = []
    for card in cards:
        data.append({
            'id': card.id,
            'client_id': card.client.id,
            'card_brand': card.card_brand,
            'card_type': card.card_type,
            'card_number': card.card_number,
            'expires': card.expires,
            'has_chip': card.has_chip,
            'num_cards_issued': card.num_cards_issued,
            'credit_limit': float(card.credit_limit) if card.credit_limit else None,
        })
    return JsonResponse({'cards': data})


@csrf_exempt
@require_http_methods(["GET"])
def api_transactions(request):
    """API endpoint to get all transactions"""
    transactions = Transaction.objects.select_related('client', 'card').all()[:25]
    data = []
    for transaction in transactions:
        data.append({
            'id': transaction.id,
            'date': transaction.date.isoformat(),
            'client_id': transaction.client.id,
            'card_id': transaction.card.id,
            'amount': float(transaction.amount),
            'use_chip': transaction.use_chip,
            'merchant_id': transaction.merchant_id,
            'merchant_city': transaction.merchant_city,
            'merchant_state': transaction.merchant_state,
            'zip': transaction.zip,
        })
    return JsonResponse({'transactions': data})


@csrf_exempt
@require_http_methods(["GET"])
def api_mindsdb_wealthy_clients(request):
    """API endpoint to find wealthy clients using MindsDB semantic search"""
    try:
        min_age = int(request.GET.get('min_age', 40))
        min_income = float(request.GET.get('min_income', 70000))
        
        results = mindsdb_util.find_wealthy_clients(min_age=min_age, min_income=min_income)
        
        return JsonResponse({
            'success': True,
            'query_type': 'wealthy_clients',
            'filters': {'min_age': min_age, 'min_income': min_income},
            'results': results,
            'count': len(results)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_mindsdb_travel_expenses(request):
    """API endpoint to find travel expenses using MindsDB semantic search"""
    try:
        min_amount = float(request.GET.get('min_amount', 500))
        use_chip = request.GET.get('use_chip', 'true').lower() == 'true'
        
        results = mindsdb_util.find_travel_expenses(min_amount=min_amount, use_chip=use_chip)
        
        return JsonResponse({
            'success': True,
            'query_type': 'travel_expenses',
            'filters': {'min_amount': min_amount, 'use_chip': use_chip},
            'results': results,
            'count': len(results)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_mindsdb_online_shopping(request):
    """API endpoint to find online shopping transactions using MindsDB semantic search"""
    try:
        state = request.GET.get('state', 'California')
        
        results = mindsdb_util.find_online_shopping(state=state)
        
        return JsonResponse({
            'success': True,
            'query_type': 'online_shopping',
            'filters': {'state': state},
            'results': results,
            'count': len(results)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_mindsdb_suspicious_transactions(request):
    """API endpoint to find suspicious transactions with AI summaries"""
    try:
        results = mindsdb_util.find_suspicious_transactions()
        
        return JsonResponse({
            'success': True,
            'query_type': 'suspicious_transactions',
            'results': results,
            'count': len(results)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_mindsdb_unusual_spending(request):
    """API endpoint to find unusual spending patterns with AI summaries"""
    try:
        results = mindsdb_util.find_unusual_spending()
        
        return JsonResponse({
            'success': True,
            'query_type': 'unusual_spending',
            'results': results,
            'count': len(results)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_mindsdb_custom_search(request):
    """API endpoint for custom semantic search"""
    try:
        search_term = request.GET.get('search_term', '')
        kb_type = request.GET.get('kb_type', 'transaction')
        
        if not search_term:
            return JsonResponse({
                'success': False,
                'error': 'search_term parameter is required'
            }, status=400)
        
        # Parse filters from query parameters
        filters = {}
        for key, value in request.GET.items():
            if key.startswith('filter_'):
                filter_key = key[7:]  # Remove 'filter_' prefix
                # Try to convert to appropriate type
                try:
                    if value.lower() in ['true', 'false']:
                        filters[filter_key] = value.lower() == 'true'
                    elif '.' in value:
                        filters[filter_key] = float(value)
                    else:
                        filters[filter_key] = int(value)
                except ValueError:
                    filters[filter_key] = value
        
        results = mindsdb_util.custom_semantic_search(
            search_term=search_term,
            kb_type=kb_type,
            filters=filters if filters else None
        )
        
        return JsonResponse({
            'success': True,
            'query_type': 'custom_search',
            'search_term': search_term,
            'kb_type': kb_type,
            'filters': filters,
            'results': results,
            'count': len(results)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_mindsdb_stats(request):
    """API endpoint to get MindsDB knowledge base statistics"""
    try:
        stats = mindsdb_util.get_knowledge_base_stats()
        connection_status = mindsdb_util.test_connection()
        
        return JsonResponse({
            'success': True,
            'connection_status': connection_status,
            'knowledge_base_stats': stats
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_mindsdb_execute_query(request):
    """API endpoint to execute custom MindsDB SQL queries"""
    try:
        import json
        data = json.loads(request.body)
        query = data.get('query', '')
        
        if not query:
            return JsonResponse({
                'success': False,
                'error': 'query parameter is required'
            }, status=400)
        
        results = mindsdb_util.execute_query(query)
        
        return JsonResponse({
            'success': True,
            'query': query,
            'results': results,
            'count': len(results)
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def mindsdb_dashboard(request):
    """MindsDB Knowledge Base Dashboard view"""
    return render(request, 'finance/mindsdb_dashboard.html')
