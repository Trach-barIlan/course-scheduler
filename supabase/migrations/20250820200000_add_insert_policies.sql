-- Add INSERT policies to allow data migration
-- These policies allow public INSERT access for migration purposes
-- In production, you may want to restrict these further

-- Allow INSERT access for data migration
CREATE POLICY "Allow public insert access on universities" ON universities FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public insert access on departments" ON departments FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public insert access on courses" ON courses FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public insert access on course_events" ON course_events FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public insert access on lecturers" ON lecturers FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public insert access on locations" ON locations FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public insert access on time_slots" ON time_slots FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public insert access on course_materials" ON course_materials FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public insert access on course_prerequisites" ON course_prerequisites FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public insert access on course_event_lecturers" ON course_event_lecturers FOR INSERT WITH CHECK (true);

-- Allow UPDATE access for UPSERT operations during migration
CREATE POLICY "Allow public update access on universities" ON universities FOR UPDATE USING (true) WITH CHECK (true);
CREATE POLICY "Allow public update access on departments" ON departments FOR UPDATE USING (true) WITH CHECK (true);
CREATE POLICY "Allow public update access on courses" ON courses FOR UPDATE USING (true) WITH CHECK (true);
CREATE POLICY "Allow public update access on course_events" ON course_events FOR UPDATE USING (true) WITH CHECK (true);
CREATE POLICY "Allow public update access on lecturers" ON lecturers FOR UPDATE USING (true) WITH CHECK (true);
CREATE POLICY "Allow public update access on locations" ON locations FOR UPDATE USING (true) WITH CHECK (true);
CREATE POLICY "Allow public update access on time_slots" ON time_slots FOR UPDATE USING (true) WITH CHECK (true);
CREATE POLICY "Allow public update access on course_materials" ON course_materials FOR UPDATE USING (true) WITH CHECK (true);
CREATE POLICY "Allow public update access on course_prerequisites" ON course_prerequisites FOR UPDATE USING (true) WITH CHECK (true);
CREATE POLICY "Allow public update access on course_event_lecturers" ON course_event_lecturers FOR UPDATE USING (true) WITH CHECK (true);
