import decimal

from django.contrib.auth.decorators import login_required
from django.template.loader import get_template, render_to_string

from .models import *
from .forms import *
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.db.models import Sum
from django.http import HttpResponse
from .utils import render_to_pdf
from django.core.mail import EmailMultiAlternatives



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
    # Loop through each stock and add the value to the total
    for stock in stocks:
        sum_current_stocks_value += stock.current_stock_value()
        sum_of_initial_stock_value += stock.initial_stock_value()

    result = decimal.Decimal(sum_current_stocks_value) - (sum_of_initial_stock_value)

    for investment in investments:
        sum_current_investment_value += investment.recent_value
        sum_of_initial_investment_value += investment.acquired_value

    result1 = sum_current_investment_value - sum_of_initial_investment_value
    Total_current_investments = float(sum_current_stocks_value) + float(sum_current_investment_value)
    Total_initial_investmensts = float(sum_of_initial_investment_value) + float(sum_of_initial_stock_value)
    Grand_total = result + result1

    return render(request,'portfolio/portfolio.html', {'customer': customer,'customers': customers,
               'investments': investments,
               'stocks': stocks,
               'sum_acquired_value': sum_acquired_value,
               'sum_recent_value': sum_recent_value,
               'result': result,
               'sum_current_stocks_value': sum_current_stocks_value,
               'sum_of_initial_stock_value': sum_of_initial_stock_value,
               'sum_current_investment_value': sum_current_investment_value,
               'sum_of_initial_investment_value': sum_of_initial_investment_value,
               'result1': result1,
               'Total_current_investments': Total_current_investments,
               'Total_initial_investmensts': Total_initial_investmensts,
               'Grand_total': Grand_total});

def generate_pdf_view(request,pk, *args, **kwargs):
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

    result = decimal.Decimal(sum_current_stocks_value) - (sum_of_initial_stock_value)

    for investment in investments:
        sum_current_investment_value += investment.recent_value
        sum_of_initial_investment_value += investment.acquired_value

    result1 = sum_current_investment_value - sum_of_initial_investment_value

    Total_current_investments = float(sum_current_stocks_value) + float(sum_current_investment_value)
    Total_initial_investmensts = float(sum_of_initial_investment_value) + float(sum_of_initial_stock_value)
    Grand_total = result + result1

    template = get_template('portfolio/Pdf.html')
    context = {
               'customers' : customers,
                'investments': investments,
                'stocks': stocks,
                'sum_acquired_value': sum_acquired_value,
                'sum_recent_value': sum_recent_value,
                'result': result,
                'sum_current_stocks_value': sum_current_stocks_value,
                'sum_of_initial_stock_value': sum_of_initial_stock_value,
                'sum_current_investment_value':sum_current_investment_value,
                'sum_of_initial_investment_value':sum_of_initial_investment_value,
                'result1':result1,
                'Total_current_investments':Total_current_investments,
                'Total_initial_investmensts': Total_initial_investmensts,
                'Grand_total':Grand_total}
    html = template.render(context)
    pdf = render_to_pdf('portfolio/Pdf.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "customer_%s.pdf" % ("portfolio")
        content = "inline; filename=%s" %(filename)
        download = request.GET.get("download")
        print('888888888888888')
        if download:
            content = "attachment; filename= %s" %(filename)
        response['Content-Disposition'] = content
        return response

    return HttpResponse("Not found")
