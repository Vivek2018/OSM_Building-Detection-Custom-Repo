class Rectangle:
    current_id = 0
    # do rectangles try to merge with neighboring rectangles?
    # list of all rectangles in existence
    all_rects = []
    all_rect_ids = []
    deleted_rect_ids = []
    tolerable_distance_to_combine_rectangles = 0.00005  # buildings need to be this (lat/long degrees) away to merge

    def __init__(self, init_points, to_id=True):
        self.points = init_points  # a point is a list, in (lat, long) form
        Rectangle.current_id += 1
        self.id = Rectangle.current_id
        if to_id:
            Rectangle.add_rect(self)

    def merge_with(self, other_rectangle):
        for point in other_rectangle.points:
            # if the rectangles overlap
            if self.has_point_inside_approx(point):
                # get cords for the merged rectangle
                top = min(self.get_up_bound(), other_rectangle.get_up_bound())
                bot = max(self.get_down_bound(), other_rectangle.get_down_bound())
                right = max(self.get_right_bound(), other_rectangle.get_right_bound())
                left = min(self.get_left_bound(), other_rectangle.get_left_bound())

                # delete both rectangles
                Rectangle.delete_rect(other_rectangle.get_id())
                Rectangle.delete_rect(self.get_id())

                # make a new merged rectangle
                return Rectangle([[right, top], [left, top], [left, bot], [right, bot]])
        return None

    # Checks if a point is inside/on the borders
    def has_point_inside(self, point_to_check):
        has_up_bound, has_down_bound, has_left_bound, has_right_bound = False, False, False, False
        # check all lines in this rectangle -> does the point lay in between 4 lines?
        for i in range(0, len(self.points)):
            point1 = self.points[i]
            point2 = self.points[(i + 1) % len(self.points)]
            # if vertical line
            if point1[0] == point2[0]:
                if point1[1] < point_to_check[1] < point2[1] or point1[1] > point_to_check[1] > point2[1]:
                    # point_to_check is within the y-range of the line
                    if point_to_check[0] >= point1[0]:
                        has_left_bound = True
                    if point_to_check[0] <= point1[0]:
                        has_right_bound = True
            # if horizontal line
            if point1[1] == point2[1]:
                if point1[0] < point_to_check[0] < point2[0] or point1[0] > point_to_check[0] > point2[0]:
                    # point_to_check is within the x-domain of the line
                    if point_to_check[1] >= point1[1]:
                        has_down_bound = True
                    if point_to_check[1] <= point1[1]:
                        has_up_bound = True
        return has_up_bound and has_down_bound and has_left_bound and has_right_bound

    # check if point is close enough to be inside by shifting the point up, down, left, right
    def has_point_inside_approx(self, point_to_check, tolerable_distance=tolerable_distance_to_combine_rectangles):
        if tolerable_distance == 0:
            return self.has_point_inside(point_to_check)
        slide_right = self.has_point_inside((point_to_check[0] + tolerable_distance, point_to_check[1]))
        slide_left = self.has_point_inside((point_to_check[0] - tolerable_distance, point_to_check[1]))
        slide_up = self.has_point_inside((point_to_check[0], point_to_check[1] - tolerable_distance))
        slide_down = self.has_point_inside((point_to_check[0], point_to_check[1] + tolerable_distance))
        stay_put = self.has_point_inside(point_to_check)
        return slide_right or slide_left or slide_up or slide_down or stay_put

    # returns leftmost x cord
    def get_left_bound(self):
        left_bound = self.points[0][0]
        for point in self.points:
            if point[0] < left_bound:
                left_bound = point[0]
        return left_bound

    # returns rightmost x cord
    def get_right_bound(self):
        right_bound = self.points[0][0]
        for point in self.points:
            if point[0] > right_bound:
                right_bound = point[0]
        return right_bound

    # returns smallest y cord
    def get_up_bound(self):
        up_bound = self.points[0][1]
        for point in self.points:
            if point[1] < up_bound:
                up_bound = point[1]
        return up_bound

    # returns largest y cord
    def get_down_bound(self):
        down_bound = self.points[0][1]
        for point in self.points:
            if point[1] > down_bound:
                down_bound = point[1]
        return down_bound

    def get_id(self):
        return self.id

    def get_points(self):
        return self.points

    # updating the static added_rectangles and removed_rectangles lists
    @staticmethod
    def add_rect(rect):
        Rectangle.all_rects.append(rect)
        Rectangle.all_rect_ids.append(rect)

    @staticmethod
    def get_all_rects():
        return Rectangle.all_rects

    @staticmethod
    def get_rect(rect_id):
        if rect_id < len(Rectangle.all_rects):
            return Rectangle.all_rects[rect_id - 1]
        return None

    # convert a list of rectangles into a list of rectangle ids
    @staticmethod
    def arr_rect_to_id(rect_arr):
        id_arr = []
        for rect in rect_arr:
            id_arr.append(rect.get_id())
        return id_arr

    @staticmethod
    def delete_rect(rect_id):
        if rect_id in Rectangle.all_rect_ids:
            print("deleting rect", rect_id)
            Rectangle.all_rects.remove(rect_id)
            Rectangle.deleted_rect_ids.append(rect_id)
            return True
        return False

    @staticmethod
    def get_deleted_rects():
        copy = Rectangle.deleted_rect_ids
        Rectangle.deleted_rect_ids = []
        return copy

    # reset all internal storage of rectangle objects
    @staticmethod
    def delete_all_rects():
        Rectangle.all_rects = []
        Rectangle.all_rect_ids = []
        Rectangle.current_id = 0

# def get_all_rects_dictionary():
#     rect_dict = {}
#     for rect in Rectangle.all_rects:
#         rect_dict[rect.get_id()] = rect.get_points()
#     return rect_dict
