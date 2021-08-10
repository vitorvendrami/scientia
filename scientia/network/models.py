import uuid
from django.db import models
from django.contrib.auth.models import User
import gurobipy as gp
import numpy as np
import itertools
import pandas as pd
from django.contrib.postgres.fields import ArrayField

class NetworkModel(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    def __init__(self, Env):
        self.num_p = Env.num_p
        self.num_i = Env.num_i
        self.num_j = Env.num_j
        self.PxIxJ = list(itertools.product(range(self.num_p), range(self.num_i), range(self.num_j)))
        self.PxJ = list(itertools.product(range(self.num_p), range(self.num_j)))
        self.PxI = list(itertools.product(range(self.num_p), range(self.num_i)))
        self.IxJ = list(itertools.product(range(self.num_i), range(self.num_j)))
        self.transp_cost = Env.transp_cost
        self.prod_cost = Env.prod_cost
        self.demand = Env.demand
        self.supply = Env.supply
        self.space = Env.space
        self.flow_cap = Env.flow_cap

    def create_variables(self):
        self.assign = {(p, i, j): self.model.addVar(vtype=gp.GRB.INTEGER, name='assign_{0}_{1}_{2}'.format(p, i, j))
                       for p, i, j in self.PxIxJ}

    def set_objective(self):
        self.objective = gp.quicksum(
            self.transp_cost[p, i, j] * self.assign[p, i, j] + self.prod_cost[p, i] * self.assign[p, i, j] for
            p, i, j in self.PxIxJ)
        self.model.ModelSense = gp.GRB.MINIMIZE
        self.model.setObjective(self.objective)

    def create_demand_constraint(self):
        self.demand_constraint = {(p, j):
            self.model.addLConstr(
                lhs=gp.quicksum(self.assign[p, i, j] for i in range(self.num_i)),
                sense=gp.GRB.GREATER_EQUAL,
                rhs=self.demand[p, j],
                name="Demand_constraint_{0}_{1}".format(p, j))
            for p, j in self.PxJ}

    def create_supply_constraint(self):
        self.supply_constraint = {(p, i):
            self.model.addLConstr(
                lhs=gp.quicksum(self.assign[p, i, j] for j in range(self.num_j)),
                sense=gp.GRB.LESS_EQUAL,
                rhs=self.supply[p, i],
                name="Supply_constraint_{0}_{1}".format(p, i))
            for p, i in self.PxI}

    def create_flow_constraint(self):
        self.transp_constraint = {(i, j):
            self.model.addLConstr(
                lhs=gp.quicksum(self.space[p] * self.assign[p, i, j] for p in range(self.num_p)),
                sense=gp.GRB.LESS_EQUAL,
                rhs=self.flow_cap[i, j],
                name="Flow_constraint_{0}_{1}".format(i, j))
            for i, j in self.IxJ}

    def solve_model(self):
        self.model.optimize()
        print('\n\nModel status:')
        print(self.model.status)

    def get_solution(self):
        self.assign_df = pd.DataFrame.from_dict(self.assign, orient="index", columns=["variable_object"])
        self.assign_df.index = pd.MultiIndex.from_tuples(self.assign_df.index,
                                                         names=["Product", "Origins", "Destinations"])
        self.assign_df.reset_index(inplace=True)
        self.assign_df["Transported"] = self.assign_df["variable_object"].apply(lambda item: item.x)
        self.assign_df.drop(columns=["variable_object"], inplace=True)

        print('\nTotal Cost:')
        print(self.model.getObjective().getValue())

    def run(self):
        self.model = gp.Model(name="Network model")
        self.create_variables()
        self.set_objective()
        self.create_demand_constraint()
        self.create_supply_constraint()
        self.create_flow_constraint()
        self.solve_model()
        self.get_solution()


class GenerateEnvironment(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

    p_tuple = ArrayField(
            models.FloatField(blank=True),
            size=2,
            help_text="p_tuple Ex: 1, 2 "
    )
    i_tuple = ArrayField(
            models.FloatField(blank=True),
            size=2,
            help_text="i_tuple Ex: 1, 2 "
    )
    j_tuple = ArrayField(
            models.FloatField(blank=True),
            size=2,
            help_text="j_tuple Ex: 1, 2 "
    )
    tc_tuple = ArrayField(
            models.FloatField(blank=True),
            size=2,
            help_text="tc_tuple Ex: 1, 2 "
    )
    pc_tuple = ArrayField(
            models.FloatField(blank=True),
            size=2,
            help_text="pc_tuple Ex: 1, 2 "
    )
    fc_tuple = ArrayField(
            models.FloatField(blank=True),
            size=2,
            help_text="fc_tuple Ex: 1, 2 "
    )
    demand_tuple = ArrayField(
            models.FloatField(blank=True),
            size=2,
            help_text="demand_tuple Ex: 1, 2 "
    )
    space_tuple = ArrayField(
            models.FloatField(blank=True),
            size=2,
            help_text="space_tuple Ex: 1, 2 "
    )

    num_p = models.SmallIntegerField(blank=True, null=True)
    num_i = models.SmallIntegerField(blank=True, null=True)
    num_j = models.SmallIntegerField(blank=True, null=True)


    class Meta:

        verbose_name = "GenerateEnvironment"
        verbose_name_plural = "GenerateEnvironments"

    def __str__(self):
        return str(self.uuid)

    @classmethod
    def generate_tuples(cls, p_tuple):
        tuples = {}

        qs = cls.objects.get(p_tuple=p_tuple)

    @classmethod
    def generate_num_items(cls, uuid):
        qs = cls.objects.get(uuid=uuid)
        num_p = np.random.randint(qs.p_tuple[0], qs.p_tuple[1])
        num_i = np.random.randint(qs.i_tuple[0], qs.i_tuple[1])
        num_j = np.random.randint(qs.j_tuple[0], qs.j_tuple[1])
        print("Randomized results:")
        print("Number of Products: " + str(num_p))
        print("Number of Origins: " + str(num_i))
        print("Number of Destinations: " + str(num_j))
        qs.num_p = num_p
        qs.num_i = num_i
        qs.num_j = num_j
        qs.save()

        return num_p, num_i, num_j

    @classmethod
    def generate_costs(cls, uuid):
        qs = cls.objects.get(uuid=uuid)
        transp_cost = np.random.uniform(qs.tc_tuple[0], qs.tc_tuple[1], size=(qs.num_p, qs.num_i, qs.num_j))
        prod_cost = np.random.uniform(qs.pc_tuple[0], qs.pc_tuple[1], size=(qs.num_p, qs.num_i))
        fixed_cost = np.random.uniform(qs.fc_tuple[0], qs.fc_tuple[1], size=qs.num_i)

        return transp_cost, prod_cost, fixed_cost

    @classmethod
    def generate_demand(cls, uuid):
        qs = cls.objects.get(uuid=uuid)
        demand = np.random.randint(qs.demand_tuple[0], qs.demand_tuple[1], size=(qs.num_p, qs.num_j))
        return demand

    @classmethod
    def generate_supply(cls, uuid, demand):
        qs = cls.objects.get(uuid=uuid)
        supply = np.empty([qs.num_p, qs.num_i])
        total_dem = demand.sum(1)
        for p in range(qs.num_p):
          p_dem = total_dem[p]
          supply[p] = np.random.randint(p_dem/qs.num_i, p_dem/(qs.num_i - 1), size=(qs.num_i)) + 1

        return supply

    @classmethod
    def generate_space(cls, uuid):
        qs = cls.objects.get(uuid=uuid)
        space = np.random.uniform(qs.space_tuple[0], qs.space_tuple[1], size=qs.num_p)
        return space

    @classmethod
    def generate_flow(cls, uuid, demand, space, supply):
        qs = cls.objects.get(uuid=uuid)

        d_flow_cap = np.empty([qs.num_i, qs.num_j])
        demand_space = np.dot(space, demand)
        for j in range(qs.num_j):
          ds = demand_space[j]
          d_flow_cap[:, j] = np.random.randint(ds/qs.num_i, ds/(qs.num_i - 1) + 1, size = (qs.num_i)) + 1

        s_flow_cap = np.empty([qs.num_i, qs.num_j])
        supply_space = np.dot(space, supply)
        for i in range(qs.num_i):
          ss = supply_space[i]
          s_flow_cap[i] = np.random.randint(ss/qs.num_j, ss/(qs.num_j - 1) + 1, size = (qs.num_j)) + 1
        flow_cap = np.maximum(d_flow_cap, s_flow_cap)
        return flow_cap

    @classmethod
    def run(self, uuid):
        num_p, num_i, num_j = self.generate_num_items(uuid)
        transp_cost, prod_cost, fixed_cost = self.generate_costs(uuid)
        demand = self.generate_demand(uuid)
        supply = self.generate_supply(uuid, demand)
        space = self.generate_space(uuid)
        flow_cap = self.generate_flow(uuid, demand, space, supply)

        return {

            "transp_cost": transp_cost,
            "prod_cost": prod_cost,
            "fixed_cost": fixed_cost,
            "demand": demand,
            "supply": supply,
            "space": space,
            "flow_cap": flow_cap
        }

# class RequestOrder(models.Model):
#     uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
#     request_number = models.CharField("Request Number", max_length=30, default="0")
#     client = models.ForeignKey(Client, on_delete=models.CASCADE)
#     seller = models.ForeignKey(Supplier, on_delete=models.CASCADE)
#     payment_option = models.CharField(
#         "Opção de Pagamento",
#         choices=PAYMENT_OPTION_CHOICES,
#         max_length=20,
#         default="deposit",
#     )
#     change = models.DecimalField("Troco", default=0, decimal_places=2, max_digits=8)
#     active_client = models.BooleanField(default=True)
#     active_seller = models.BooleanField(default=True)
#     status = models.CharField(
#         max_length=180, choices=STATUS_CHOICES, default="Pedido Realizado"
#     )
#     active = models.BooleanField(default=True)
#     opening_date = models.DateField(auto_now_add=True)
#     update_date = models.DateField(auto_now=True)
#
#     class Meta:
#         verbose_name = "Pedido"
#         verbose_name_plural = "Pedidos"
#
#     def __str__(self):
#         return "Pedido de {} numero {}".format(self.client.user.username, self.pk)
#
#     def products(self):
#         products_ids = self.items.values_list("product")
#         return Product.objects.filter(pk__in=products_ids)
#
#     def total(self):
#         aggregate_queryset = self.items.aggregate(
#             total=models.Sum(
#                 models.F("price") * models.F("quantity"),
#                 output_field=models.DecimalField(),
#             )
#         )
#         return aggregate_queryset["total"]
#
#     objects = OrderManager()