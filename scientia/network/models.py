import uuid
from django.db import models
from django.contrib.auth.models import User
import numpy as np
from django.contrib.postgres.fields import ArrayField


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

