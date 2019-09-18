from collections import defaultdict

class Abcd:

    def __init__(self, rx = "rx", data = "data"):
        self.known = defaultdict(int)
        self.a = defaultdict(int)
        self.b = defaultdict(int)
        self.c = defaultdict(int)
        self.d = defaultdict(int)
        self.rx = rx
        self.data = data
        self.yes = self.no = 0


    def abcd1(self, want, got):

        self.known[want] += 1
        if self.known[want] == 1:
            self.a[want] = self.yes + self.no

        self.known[got] += 1
        if self.known[got] == 1:
            self.a[got] = self.yes + self.no

        if want == got:
            self.yes += 1
        else:
            self.no += 1
        
        for x in self.known:
            if want == x:
                if want == got:
                    self.d[x] += 1
                else:
                    self.b[x] += 1
            else:
                if x == got:
                    self.c[x] += 1
                else:
                    self.a[x] += 1 

    def abcd_report(self):

        print ("db\t|\trx\t|\tnum\t|\ta\t|\tb\t|\tc\t|\td\t|\tacc\t|\tprec\t|\tpd\t|\tpf\t|\tf\t|\tg\t|\tclass")
        for each_class in self.known:
            a,b,c,d = self.a[each_class], self.b[each_class], self.c[each_class], self.d[each_class]
            accuracy = float(self.yes) / (self.yes + self.no) if (self.yes + self.no) > 0 else 0
            precision = self.precision(c,d)
            recall = self.recall(b,d)
            false_alarm = self.false_alarm(a,c)
            f_score = self.f_measure(precision,recall)
            g_score = self.g_measure(false_alarm,recall)

            print ("{0}\t|\t{1}\t|\t{2}\t|\t{3}\t|\t{4}\t|\t{5}\t|\t{6}\t|\t{7}\t|\t{8}\t|\t{9}\t|\t{10}\t|\t{11}\t|\t{12}\t|\t{13}"\
                    .format(self.data, self.rx,(self.yes + self.no), a,b,c,d,round(accuracy,2),\
                    round(precision,2),round(recall,2),round(false_alarm,2),round(f_score,2),\
                    round(g_score,2),each_class))


    def recall(self, b, d):
        return float(d) / (b + d) if (b + d) > 0 else 0
    

    def precision(self, c, d):
        return float(d) / (c + d) if (c + d) > 0 else 0


    def false_alarm(self, a, c):
        return float(c) / (a + c) if (a + c) > 0 else 0
    

    def f_measure(self, precision,recall):
        return 2*precision*recall / (precision + recall) if (precision + recall) > 0 else 0
    

    def g_measure(self, false_alarm, recall):
        return 2*(1 - false_alarm)*recall / (1 - false_alarm + recall) if (1 - false_alarm + recall) > 0 else 0



if __name__ == "__main__":
    
    abcd = Abcd()
    for _ in range(6):  abcd.abcd1("yes","yes")
    for _ in range(2):  abcd.abcd1("no","no")
    for _ in range(5):  abcd.abcd1("maybe","maybe")
    abcd.abcd1("maybe","no")
    abcd.abcd_report()