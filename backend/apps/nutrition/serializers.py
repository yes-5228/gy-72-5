from decimal import Decimal

from rest_framework import serializers

from apps.menu.models import Dish
from apps.menu.serializers import DishSerializer


class DishWithQuantitySerializer(serializers.Serializer):
    dish_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1, default=1)


class NutritionAnalysisRequestSerializer(serializers.Serializer):
    dish_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=True,
        required=False,
    )
    items = serializers.ListField(
        child=DishWithQuantitySerializer(),
        allow_empty=True,
        required=False,
    )

    def validate(self, attrs):
        if not attrs.get("dish_ids") and not attrs.get("items"):
            raise serializers.ValidationError("请提供 dish_ids 或 items 参数。")
        return attrs


class NutritionAnalysisSerializer(serializers.Serializer):
    dishes = DishSerializer(many=True)
    totals = serializers.DictField()
    advice = serializers.ListField(child=serializers.CharField())


def analyze_dishes(dish_ids=None, items=None):
    quantity_map = {}
    if items:
        for item in items:
            quantity_map[item["dish_id"]] = quantity_map.get(item["dish_id"], 0) + item.get("quantity", 1)
    elif dish_ids:
        for did in dish_ids:
            quantity_map[did] = quantity_map.get(did, 0) + 1

    dish_ids_list = list(quantity_map.keys())
    dishes = list(Dish.objects.filter(id__in=dish_ids_list).select_related("category"))
    dish_by_id = {d.id: d for d in dishes}

    totals = {
        "calories": 0,
        "protein": Decimal("0"),
        "fat": Decimal("0"),
        "carbohydrate": Decimal("0"),
        "sodium": 0,
    }
    for dish_id, qty in quantity_map.items():
        dish = dish_by_id.get(dish_id)
        if not dish:
            continue
        totals["calories"] += dish.calories * qty
        totals["protein"] += Decimal(dish.protein) * qty
        totals["fat"] += Decimal(dish.fat) * qty
        totals["carbohydrate"] += Decimal(dish.carbohydrate) * qty
        totals["sodium"] += dish.sodium * qty

    totals = {key: float(value) if isinstance(value, Decimal) else value for key, value in totals.items()}

    advice = []
    if totals["calories"] < 550:
        advice.append("本餐热量偏低，适合加一份主食或高蛋白菜品。")
    elif totals["calories"] > 900:
        advice.append("本餐热量偏高，建议减少油炸或高碳水菜品。")
    else:
        advice.append("本餐热量处于常规午/晚餐区间。")

    if totals["protein"] < 25:
        advice.append("蛋白质略少，可补充鸡蛋、鱼肉、豆制品等。")
    if totals["sodium"] > 1800:
        advice.append("钠含量偏高，建议搭配清淡汤品并减少调味酱。")
    if not advice:
        advice.append("营养搭配均衡。")

    return {"dishes": dishes, "totals": totals, "advice": advice}
