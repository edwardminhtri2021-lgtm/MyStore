from django.shortcuts import render
from store.models import Order
from django.conf import settings
from datetime import datetime
import os
from xhtml2pdf import pisa

def report_home(request):
    # Giả lập admin: chỉ khi session superuser = True mới xem
    if not request.session.get('superuser', False):
        return render(request, 'storereport/no_permission.html')  # hoặc redirect về home

    return render(request, 'storereport/report_home.html')


def report_in_quarter(request):
    if not request.session.get('superuser', False):
        return render(request, 'storereport/no_permission.html')

    from store.models import Order
    from django.conf import settings
    from datetime import datetime
    import os
    from xhtml2pdf import pisa

    now = datetime.today()
    year = now.year
    month = now.month

    if month in [1,2,3]:
        start_month, end_month = 1,3
    elif month in [4,5,6]:
        start_month, end_month = 4,6
    elif month in [7,8,9]:
        start_month, end_month = 7,9
    else:
        start_month, end_month = 10,12

    orders = Order.objects.filter(
        created_at__year=year,
        created_at__month__gte=start_month,
        created_at__month__lte=end_month
    )

    data = []
    for order in orders:
        data.append({
            'OrderID': order.id,
            'Customer': order.customer_name,
            'Address': order.address,
            'TotalPrice': order.total_price,
            'CreatedAt': order.created_at,
            'Quantity': 1
        })

    quarter_number = (start_month-1)//3 +1
    context = {'orders': data, 'quarter': f"Q{quarter_number}", 'year': year}

    html_string = render(request, 'storereport/orders_report.html', context).content.decode('utf-8')

    if not os.path.exists(settings.MEDIA_ROOT):
        os.makedirs(settings.MEDIA_ROOT)

    pdf_filename = os.path.join(settings.MEDIA_ROOT, f"orders_report_q{quarter_number}_{year}.pdf")
    with open(pdf_filename, "w+b") as f:
        pisa_status = pisa.CreatePDF(html_string, dest=f)

    context['pdf_file'] = settings.MEDIA_URL + f"orders_report_q{quarter_number}_{year}.pdf"
    context['pisa_status'] = pisa_status.err

    return render(request, 'storereport/orders_report.html', context)
