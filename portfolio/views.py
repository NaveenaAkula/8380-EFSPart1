from django.core.mail import send_mail
from django.core.mail import EmailMessage
import decimal
from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.template.loader import get_template, render_to_string

from .models import *
from .forms import *
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.db.models import Sum
from django.http import HttpResponse
from .utils import render_to_pdf
from django.core.mail import EmailMultiAlternatives

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomerSerializer


# List at the end of the views.py
# Lists all customers
class CustomerList(APIView):

    def get(self, request):
        customers_json = Customer.objects.all()
        serializer = CustomerSerializer(customers_json, many=True)
        return Response(serializer.data)


now = timezone.now()


def home(request):
    return render(request, 'portfolio/home.html',
                  {'portfolio': home})


@login_required
def customer_list(request):
    customer = Customer.objects.filter(created_date__lte=timezone.now())
    return render(request, 'portfolio/customer_list.html',
                  {'customers': customer})


@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        # update
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.updated_date = timezone.now()
            customer.save()
            customer = Customer.objects.filter(created_date__lte=timezone.now())
            return render(request, 'portfolio/customer_list.html',
                          {'customers': customer})
    else:
        # edit
        form = CustomerForm(instance=customer)
    return render(request, 'portfolio/customer_edit.html', {'form': form})


@login_required
def customer_new(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.created_date = timezone.now()
            customer.save()
            customers = Customer.objects.filter(created_date__lte=timezone.now())
            return render(request, 'portfolio/customer_list.html',
                          {'customers': customers})
    else:
        form = CustomerForm()
        # print("Else")
    return render(request, 'portfolio/customer_new.html', {'form': form})


@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    return redirect('portfolio:customer_list')


@login_required
def stock_list(request):
    stocks = Stock.objects.filter(purchase_date__lte=timezone.now())
    return render(request, 'portfolio/stock_list.html', {'stocks': stocks})


@login_required
def stock_new(request):
    if request.method == "POST":
        form = StockForm(request.POST)
        if form.is_valid():
            stock = form.save(commit=False)
            stock.created_date = timezone.now()
            stock.save()
            stocks = Stock.objects.filter(purchase_date__lte=timezone.now())
            return render(request, 'portfolio/stock_list.html',
                          {'stocks': stocks})
    else:
        form = StockForm()
        # print("Else")
    return render(request, 'portfolio/stock_new.html', {'form': form})


@login_required
def stock_edit(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    if request.method == "POST":
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            stock = form.save()
            # stock.customer = stock.id
            stock.updated_date = timezone.now()
            stock.save()
            stocks = Stock.objects.filter(purchase_date__lte=timezone.now())
            return render(request, 'portfolio/stock_list.html', {'stocks': stocks})
    else:
        # print("else")
        form = StockForm(instance=stock)
    return render(request, 'portfolio/stock_edit.html', {'form': form})


@login_required
def stock_delete(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    stock.delete()
    return redirect('portfolio:stock_list')


@login_required
def investment_list(request):
    investments = Investment.objects.filter(recent_date__lte=timezone.now())
    return render(request, 'portfolio/investment_list.html', {'investments': investments})


@login_required
def investment_new(request):
    if request.method == "POST":
        form = InvestmentForm(request.POST)
        if form.is_valid():
            investment = form.save(commit=False)
            investment.created_date = timezone.now()
            investment.save()
            investments = Investment.objects.filter(recent_date__lte=timezone.now())
            return render(request, 'portfolio/investment_list.html',
                          {'investments': investments})
    else:
        form = InvestmentForm()
        # print("Else")
    return render(request, 'portfolio/investment_new.html', {'form': form})


@login_required
def investment_edit(request, pk):
    investment = get_object_or_404(Investment, pk=pk)
    if request.method == "POST":
        form = InvestmentForm(request.POST, instance=investment)
        if form.is_valid():
            investment = form.save()
            investment.updated_date = timezone.now()
            investment.save()
            investments = Investment.objects.filter(recent_date__lte=timezone.now())
            return render(request, 'portfolio/investment_list.html', {'investments': investments})
    else:
        # print("else")
        form = InvestmentForm(instance=investment)
    return render(request, 'portfolio/investment_edit.html', {'form': form})


@login_required
def investment_delete(request, pk):
    investment = get_object_or_404(Investment, pk=pk)
    investment.delete()
    return redirect('portfolio:investment_list')


@login_required
def portfolio(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customers = Customer.objects.filter(created_date__lte=timezone.now())
    investments = Investment.objects.filter(customer=pk)
    stocks = Stock.objects.filter(customer=pk)
    sum_recent_value = Investment.objects.filter(customer=pk).aggregate(Sum('recent_value'))
    sum_acquired_value = Investment.objects.filter(customer=pk).aggregate(Sum('acquired_value'))
    # overall_investment_results = sum_recent_value-sum_acquired_value
    # Initialize the value of the stocks
    sum_current_stocks_value = 0
    sum_of_initial_stock_value = 0
    sum_current_investment_value = 0
    sum_of_initial_investment_value = 0
    INR_value_stock = 0
    INR_value_investment = 0
    # Loop through each stock and add the value to the total
    for stock in stocks:
        sum_current_stocks_value += stock.current_stock_value()
        sum_of_initial_stock_value += stock.initial_stock_value()

    stock_result = decimal.Decimal(sum_current_stocks_value) - (sum_of_initial_stock_value)
    INR_value_stock = float(stock_result) * stock.currency_rate()
    for investment in investments:
        sum_current_investment_value += investment.recent_value
        sum_of_initial_investment_value += investment.acquired_value

    investment_result = sum_current_investment_value - sum_of_initial_investment_value
    INR_value_investment = float(investment_result) * stock.currency_rate()
    Total_current_investments = float(sum_current_stocks_value) + float(sum_current_investment_value)
    Total_initial_investmensts = float(sum_of_initial_investment_value) + float(sum_of_initial_stock_value)
    Total = stock_result + investment_result
    INR_Total = INR_value_stock + INR_value_investment

    return render(request, 'portfolio/portfolio.html', {'customer': customer, 'customers': customers,
                                                        'investments': investments,
                                                        'stocks': stocks,
                                                        'sum_acquired_value': sum_acquired_value,
                                                        'sum_recent_value': sum_recent_value,
                                                        'stock_result': stock_result,
                                                        'sum_current_stocks_value': sum_current_stocks_value,
                                                        'sum_of_initial_stock_value': sum_of_initial_stock_value,
                                                        'sum_current_investment_value': sum_current_investment_value,
                                                        'sum_of_initial_investment_value': sum_of_initial_investment_value,
                                                        'investment_result': investment_result,
                                                        'INR_value_stock': INR_value_stock,
                                                        'INR_value_investment': INR_value_investment,
                                                        'Total_current_investments': Total_current_investments,
                                                        'Total_initial_investmensts': Total_initial_investmensts,
                                                        'INR_Total': INR_Total,
                                                        'Total': Total});


def generate_pdf_view(request, pk, *args, **kwargs):
    customer = get_object_or_404(Customer, pk=pk)
    customers = Customer.objects.filter(created_date__lte=timezone.now())
    investments = Investment.objects.filter(customer=pk)
    stocks = Stock.objects.filter(customer=pk)
    sum_recent_value = Investment.objects.filter(customer=customer).aggregate(Sum('recent_value'))
    sum_acquired_value = Investment.objects.filter(customer=customer).aggregate(Sum('acquired_value'))
    sum_current_stocks_value = 0
    sum_of_initial_stock_value = 0
    sum_current_investment_value = 0
    sum_of_initial_investment_value = 0
    # Loop through each stock and add the value to the total
    for stock in stocks:
        sum_current_stocks_value += stock.current_stock_value()
        sum_of_initial_stock_value += stock.initial_stock_value()

    stock_result = decimal.Decimal(sum_current_stocks_value) - (sum_of_initial_stock_value)

    for investment in investments:
        sum_current_investment_value += investment.recent_value
        sum_of_initial_investment_value += investment.acquired_value

    investment_result = sum_current_investment_value - sum_of_initial_investment_value

    Total_current_investments = float(sum_current_stocks_value) + float(sum_current_investment_value)
    Total_initial_investmensts = float(sum_of_initial_investment_value) + float(sum_of_initial_stock_value)
    Total = stock_result + investment_result

    template = get_template('portfolio/Pdf.html')
    context = {
        'customers': customers,
        'investments': investments,
        'stocks': stocks,
        'sum_acquired_value': sum_acquired_value,
        'sum_recent_value': sum_recent_value,
        'stock_result': stock_result,
        'sum_current_stocks_value': sum_current_stocks_value,
        'sum_of_initial_stock_value': sum_of_initial_stock_value,
        'sum_current_investment_value': sum_current_investment_value,
        'sum_of_initial_investment_value': sum_of_initial_investment_value,
        'investment_result': investment_result,
        'Total_current_investments': Total_current_investments,
        'Total_initial_investmensts': Total_initial_investmensts,
        'Total': Total}
    html = template.render(context)
    pdf = render_to_pdf('portfolio/Pdf.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "customer_%s.pdf" % ("portfolio")
        content = "inline; filename=%s" % (filename)
        download = request.GET.get("download")
        subject, from_email, to = 'hello', 'adapanaveena2526@gmail.com', 'adapanaveena2526@gmail.com'
        text_content = 'This is an important message.'
        html_content = html_message = render_to_string('portfolio/Pdf.html', {'context': 'values'})
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        if download:
            content = "attachment; filename= %s" % (filename)
        response['Content-Disposition'] = content
        return response

    return HttpResponse("Not found")


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = PasswordChangeForm(user=request.user)
        args = {'form': form}
        return render(request, 'portfolio/change_password.html', args)


def pie_chart(request, pk):
    labels = []
    data = []
    if request.user.Role == "FA":
        customer = get_object_or_404(Customer, pk=pk)
        queryset = Stock.objects.filter(customer__cust_number=customer.cust_number)

        for stocks in queryset:
            labels.append(stocks.name)
            data.append(stocks.symbol)


        # labels2 = ["401k", "Mortagage"]
        # data2 = []
        # x = PatientEntry.objects.filter(hospital=hospital, disposition="Diagnostics").count()
        # data2.append(diagnostic)
        # surgery = PatientEntry.objects.filter(hospital=hospital, disposition="Surgery").count()
        # data2.append(surgery)
        # admitted = PatientEntry.objects.filter(hospital=hospital, disposition="Admitted Room").count()
        # data2.append(admitted)
        # discharged = PatientEntry.objects.filter(hospital=hospital, disposition="Discharged").count()
        # data2.append(discharged)
        # mortuary = PatientEntry.objects.filter(hospital=hospital, disposition="Mortuary Annex").count()
        # data2.append(mortuary)

    return render(request, 'pie_chart.html', { 'customer': customer,
        'labels': labels,
        'data': data,

    })
