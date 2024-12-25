from datetime import datetime

import factory

from storage.sqlalchemy.tables import Job
from tools.fixtures.users import UserFactory


class JobFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Job

    id = factory.Sequence(lambda n: n)
    user = factory.SubFactory(UserFactory)
    title = factory.Faker("pystr")
    description = factory.Faker("sentence")
    salary_from = factory.Faker("pyfloat", left_digits=5, right_digits=2, positive=True)
    salary_to = factory.Faker("pyfloat", left_digits=5, right_digits=2, positive=True)
    is_active = factory.Faker("pybool")
    created_at = factory.LazyFunction(datetime.utcnow)
