# utils.py
def calculate_profit(cost_price, delivery_to_customer, sale_price, platform_fee_percent=10):
    """
    Рассчитывает прибыль и маржу
    :param cost_price: цена закупки у поставщика (₽)
    :param delivery_to_customer: доставка до клиента (₽)
    :param sale_price: цена продажи (₽)
    :param platform_fee_percent: комиссия площадки (по умолчанию 10%)
    :return: словарь с данными
    """
    total_cost = cost_price + delivery_to_customer
    fee = sale_price * (platform_fee_percent / 100)
    profit = sale_price - total_cost - fee
    margin = (profit / total_cost) * 100 if total_cost > 0 else 0
    
    return {
        "cost_price": round(cost_price, 2),
        "delivery": round(delivery_to_customer, 2),
        "total_cost": round(total_cost, 2),
        "platform_fee": round(fee, 2),
        "sale_price": round(sale_price, 2),
        "profit": round(profit, 2),
        "margin": round(margin, 2)
    }
