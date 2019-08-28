import statistics
import random


class Col:
    def __init__(self):
        pass


class Num(Col):
    def __init__(self):
        super().__init__()
        self.mean = 0
        self.sd = 0
        self.all_numbers = []

    def add_new_number(self, number):
        self.all_numbers.append(number)
        self.update_mean_and_sd()

    def update_mean_and_sd(self):
        self.mean = statistics.mean(self.all_numbers) if len(self.all_numbers) > 0 else 0
        self.sd = statistics.stdev(self.all_numbers) if len(self.all_numbers) > 1 else 0

    def delete_from_behind(self):
        self.all_numbers.pop()
        self.update_mean_and_sd()


class Sym(Col):
    def __init__(self):
        super().__init__()


class Some(Col):
    def __init__(self):
        super().__init__()


def test():
    num_instance = Num()
    random.seed(13)
    random_number_list = random.sample(range(1, 1000), 100)
    cached_mean, cached_sd = [], []
    for i in range(len(random_number_list)):
        num_instance.add_new_number(random_number_list[i])
        if (i + 1) % 10 == 0:
            cached_mean.append(num_instance.mean)
            cached_sd.append(num_instance.sd)

    for i in range(99, -1, -1):
        if (i + 1) % 10 == 0:
            c_mean = cached_mean.pop()
            c_sd = cached_sd.pop()
            if num_instance.mean == c_mean and num_instance.sd == c_sd:
                print("Removed {0} elements ".format(99-i))
                print("Cached mean: {0} and incremental mean: {1}".format(c_mean, num_instance.mean))
                print("Cached SD: {0} and incremental SD: {1}".format(c_sd, num_instance.sd))
            else:
                print("Different results received")
        num_instance.delete_from_behind()
    print("Removed all elements")
    print("Incremental mean : ", num_instance.mean)
    print("Incremental SD : ", num_instance.sd)

if __name__ == "__main__":
    test()
