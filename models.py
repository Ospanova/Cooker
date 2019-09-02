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
# 	def __lt__(self, other):
# 		return order.get_diff() < other.get_diff()
	# def get_diff(self)
	# 	return self.PlanLeadTime - (self.StartTime + food.PlanLeadTime)



# class FullOrder:
# 	def __init__ (self, orderId, cookerId, status, startTime, planLeadTime, extraTime):
# 		self.orderId = orderId
# 		self.cookerId = cookerId
# 		self.status = status
# 		self.startTime = startTime
# 		self.planLeadTime = planLeadTime
# 		self.extraTime = extraTime