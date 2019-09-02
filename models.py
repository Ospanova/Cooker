class Order:
        def __init__(self, orderName, factTime):
                self.orderName = orderName
                self.factTime = factTime
        def __lt__(self, other):
                return self.factTime < other.factTime

# class OrderNew: 
# 	def __init__(self,orderId, planLeadTime, factLeadTime, factTime):
# 		self.orderId = orderId
# 		self.planLeadTime = planLeadTime
# 		self.factTime = factTime 
# 		self.factTime = factTime
# 		self.factLeadTime = factLeadTime


